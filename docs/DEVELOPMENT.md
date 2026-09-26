# Arquitectura y flujo de desarrollo

## Dos compilaciones independientes

`compose.yaml` → `scripts/container-build.sh` selecciona `RUNTIME`:

- `renpy7`: `scripts/build-renpy7.sh` ejecuta setup/build, aplica parches y
  publica el árbol del motor 7 y ELF comprimido con símbolos.
- `renpy8`: `scripts/build-renpy8.sh` ejecuta `experimental/python3/bootstrap.sh`.
  Compila CPython 3.9.21, pygame_sdl2, módulos Cython de Ren’Py 8.3.7 y soporte
  nativo. Produce `smoke.nro`, `link-probe.nro`, `agent17.nro` y sus ELF.

El lanzador C monta RomFS, registra los módulos e inicia Python. `game_entry.py`
prepara las rutas SD, recursos comunes escribibles y callbacks del lanzador.
`switch_bootstrap.py` adapta rutas, imports estáticos y procesos no disponibles.
`switch_profile.py` aplica resolución, controles y diagnóstico de entrada.

Los ZIP llevan código Python; el ELF lleva módulos nativos y bibliotecas.
Los datos del juego se leen por separado desde SD. Los parches Ren’Py 7 no se
aplican automáticamente al motor 8. Las diferencias de API y Python importan.

## macOS y compilación remota

Los comandos de Compose están en el [README](../README.md). Para un Mac donde
la emulación falle, usa Actions y descarga el artefacto del perfil correcto.
Con GitHub CLI autenticado y el repositorio clonado:

```sh
gh workflow run main.yml --repo Pamsho09/RenpySwitch --ref main
gh run list --repo Pamsho09/RenpySwitch --branch main
# Sustituye RUN_ID por la ejecución completada elegida.
gh run download RUN_ID --repo Pamsho09/RenpySwitch --name renpy-switch-renpy8 --dir artifacts-renpy8
```

Los nombres antiguos `renpy-switch-runtime` corresponden a ejecuciones previas
a la integración. Conserva commit, ID de CI, ELF y hash junto con cada entrega.

Cambios solo Python pueden reempaquetarse con el último ELF compatible;
conservar todos los parches previos del ZIP. Cambios C, Cython, CPython, SDL,
FFmpeg o enlazador requieren recompilación. Al crear un NRO, pasar **NACP y
RomFS**, y ejecutar `verify_nro.py` contra el árbol de entrada. No sustituir el
NRO si falla esta verificación. El pipeline del motor 8 ya la ejecuta.

## Conexión directa por DBI

1. Conecta Switch por USB y abre **DBI → Run MTP responder**.
2. En macOS, abre la tarjeta SD mediante un cliente MTP compatible, por ejemplo
   OpenMTP. No es un volumen montado en `/Volumes`.
3. Transfiere el NRO a `/switch/agent17/agent17-update.nro`.
4. Descarga esa copia y compara SHA-256 con el archivo local.
5. Renombra el anterior con extensión `.nro.backup` y el nuevo a `agent17.nro`.
   Conserva juegos, partidas y caché. Si falla la sustitución, restaura el nombre.
6. Cierra la sesión MTP, sal de DBI y ejecuta el juego. Regresa a MTP tras probar.

En esta sesión se automatizó con la biblioteca ARM64 Kalam incluida en
OpenMTP, usando ctypes: Initialize, FetchStorages, Walk, UploadFiles,
DownloadFiles, RenameFile y Dispose. Es una interfaz interna, no una dependencia
estable del motor. Seleccionar la SD por descripción, cerrar siempre Dispose y
no abrir dos sesiones MTP concurrentes. Los scripts locales de despliegue no
forman parte del runtime ni se requieren para copiar con el cliente gráfico.
No usar `diskutil eject` para una conexión DBI/MTP.

## Diagnóstico reproducible

Recoger de `/switch/agent17/`:

- `boot-stage.txt`: último hito del lanzador (no se actualiza por cada escena).
- `boot-errors.txt`: stderr e imports del arranque.
- `logs/log.txt`: inicialización, renderer, mandos y eventos recientes.
- `logs/traceback.txt`: excepción Python, si existe. Puede pertenecer a un arranque
  anterior; comparar contenido y hora con el log actual.

Para cierre nativo, recuperar el informe correspondiente de
`/atmosphere/crash_reports/`. No deducir frescura de fechas MTP: en esta sesión
DBI reportó fechas de 1969. El informe incluye módulo, PC y retornos. Resolver
los offsets `agent17 + 0x...` con **el ELF del mismo binario instalado**. Un
traceback Python antiguo no explica un Data Abort nuevo.

Ejemplo con las herramientas del compilador, dentro del entorno que las tenga:

```sh
aarch64-none-elf-addr2line -f -C -e agent17.elf 0xOFFSET
```

Registrar síntoma, versión, escena, botones usados, táctil, resultado, último
hito y símbolos. El guard de TLS C++ comprueba un desplazamiento específico de
la libstdc++ fijada: si cambia el toolchain hay que verificar el constructor y
la redirección a `__wrap_pthread_key_create` de nuevo.

## Alcance y pendientes

La copia de recursos comunes usa `engine-common-8.3.7/.ready`. Si se cambian
esos recursos, versionar o invalidar esa caché explícitamente; el marcador
actual evita recopiarlos. No borrar `saves/` como parte de una actualización.

El almacenamiento de TSS de Python evita las ranuras pthread para recuperar
el estado de callbacks. No demuestra que el TLS de todas las bibliotecas esté
corregido. El guard C++ también sigue siendo una mitigación. El teclado,
autoguardado, vídeos y mandos requieren pruebas completas en hardware.

No hay empaquetado NSP de Agent17 ni monitor FPS/CPU/memoria integrado y
validado. Solicitar 30 FPS no equivale a medirlos. La optimización de assets
privados se realiza fuera del repositorio; nunca subir RPA, partidas, claves,
NSP o datos del usuario al publicar cambios.
