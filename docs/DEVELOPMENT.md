# Arquitectura y flujo de desarrollo

## Dos compilaciones independientes

`compose.yaml` → `scripts/container-build.sh` selecciona `RUNTIME`:

- `renpy7`: `scripts/build-renpy7.sh` ejecuta setup/build, aplica parches y
  publica el árbol del motor 7 y ELF comprimido con símbolos.
- `renpy8`: `scripts/build-renpy8.sh` ejecuta `experimental/python3/bootstrap.sh`.
  Compila CPython 3.9.21, pygame_sdl2, módulos Cython de Ren’Py 8.3.7 y soporte
  nativo. Produce las pruebas `smoke.nro`, `link-probe.nro` y el lanzador, con sus ELF.

El lanzador C monta RomFS, registra los módulos e inicia Python. `game_entry.py`
prepara las rutas SD, recursos comunes escribibles y callbacks del lanzador.
`switch_bootstrap.py` adapta rutas, imports estáticos y procesos no disponibles.
`switch_profile.py` aplica resolución, controles y diagnóstico de entrada.

Los ZIP llevan código Python; el ELF lleva módulos nativos y bibliotecas.
Los recursos externos se leen por separado desde SD. Los parches Ren’Py 7 no se
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

Conserva commit, ID de CI, ELF y hash junto con cada entrega.
Cambios solo Python pueden reempaquetarse con el último ELF compatible;
conservar todos los parches previos del ZIP. Cambios C, Cython, CPython, SDL,
FFmpeg o enlazador requieren recompilación. Al crear un NRO, pasar NACP y
RomFS, y ejecutar `verify_nro.py` contra el árbol de entrada. No sustituir el
NRO si falla esta verificación. El pipeline del motor 8 ya la ejecuta.

## Conexión directa por DBI

1. Conecta Switch por USB y abre **DBI → Run MTP responder**.
2. En macOS, abre la tarjeta SD mediante un cliente MTP compatible.
   No es un volumen montado en `/Volumes`.
3. Consulta las rutas fijas de `game_entry.py` y `game_main.c` y transfiere el
   NRO a esa carpeta con un nombre temporal.
4. Descarga esa copia y compara SHA-256 con el archivo local.
5. Conserva el NRO anterior con extensión `.nro.backup` y renombra el nuevo
   con el nombre de instalación. Conserva recursos, guardados y caché.
6. Cierra la sesión MTP, sal de DBI y ejecuta el lanzador.

No abrir dos sesiones MTP concurrentes ni usar `diskutil eject` para DBI/MTP.
Si falla la sustitución, restaura el nombre del NRO anterior.

## Diagnóstico reproducible

Recoger de la carpeta del lanzador:

- `boot-stage.txt`: último hito del lanzador.
- `boot-errors.txt`: stderr e imports del arranque.
- `logs/log.txt`: inicialización, renderer, mandos y eventos recientes.
- `logs/traceback.txt`: excepción Python, si existe. Puede pertenecer a un arranque
  anterior; comparar contenido y hora con el log actual.

Para cierre nativo, recuperar el informe correspondiente de
`/atmosphere/crash_reports/`. No deducir frescura solo de fechas MTP.
El informe incluye módulo, PC y retornos. Resolver offsets con el ELF del
mismo binario instalado; un traceback antiguo no explica un Data Abort nuevo.

Ejemplo, sustituyendo `LANZADOR.elf` por el ELF de la compilación instalada:

```sh
aarch64-none-elf-addr2line -f -C -e LANZADOR.elf 0xOFFSET
```

Registrar síntoma, versión, pasos de reproducción, botones usados, táctil,
resultado, último hito y símbolos. El guard de TLS C++ comprueba un
desplazamiento específico de la libstdc++ fijada: si cambia el toolchain,
verificar el constructor y la redirección a `__wrap_pthread_key_create`.

## Alcance y pendientes

La copia de recursos comunes usa `engine-common-8.3.7/.ready`. Si se cambian
esos recursos, versionar o invalidar esa caché explícitamente; el marcador
actual evita recopiarlos. No borrar `saves/` como parte de una actualización.

El almacenamiento de TSS de Python evita las ranuras pthread para recuperar
el estado de callbacks. No demuestra que el TLS de todas las bibliotecas esté
corregido. El guard C++ también sigue siendo una mitigación. El teclado,
autoguardado, vídeos y mandos requieren pruebas completas en hardware.

El empaquetado NSP y el monitor FPS/CPU/memoria no están integrados y validados
para el motor 8. Solicitar 30 FPS no equivale a medirlos.

## Herramientas de vídeo

Reducir la salida del renderer no reduce la resolución que FFmpeg debe
decodificar. Las herramientas permiten preparar overrides VP8 conservando audio:

```sh
python3 tools/assets/transcode_webm_overrides.py /ruta/game/archive.rpa /ruta/overrides --ffmpeg /ruta/ffmpeg --width 960 --height 540 --fps 30 --bitrate 1400k
python3 tools/assets/video_sizes.py /ruta/game/archive.rpa /ruta/overrides/switch-video-sizes.json
```

Copiar el árbol `movie/` y `switch-video-sizes.json` a `game/` para la prueba.
Antes de reemplazar overrides existentes, respaldarlos. El manifiesto de la
conversión contiene hashes. Mantener los recursos externos fuera del repositorio.
El perfil del motor 8 usa los metadatos para conservar el tamaño original de
Movie cuando no se declara un tamaño; mantiene tamaños explícitos y ajusta
la anchura de máscaras laterales. Sin metadatos, no altera el tamaño.
La reducción implica menor detalle y requiere validación visual en hardware.

## Extensión opcional

`experimental/python3/switch_urm_compat.rpy` proporciona un hook de
compatibilidad para una extensión suministrada por separado. Ejecuta init 998
para desactivar la comprobación automática de red antes de init 999.
Requiere un NRO que contenga `skip_urm_update`. Mantener L+R y pulsar X abre
Alt+M cuando `x52URM.Open` existe; si falta, muestra un aviso.
El lanzador expone `__main__.path_to_saves` para sus ajustes. El hook y el
atajo no incluyen ni instalan la extensión; su menú requiere prueba en hardware.
