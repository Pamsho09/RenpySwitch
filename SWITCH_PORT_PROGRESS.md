# Estado del port — 26 de septiembre de 2026

`main` integra `renpy8-native-bootstrap` y `switch-audio-tls-experiment` por
solicitud del propietario. Ambos motores siguen siendo experimentales.

## Ren’Py 8 / Agent17 0.25.9

| Etapa | Resultado / evidencia |
| --- | --- |
| CPython, biblioteca estándar y 66 módulos nativos | Imports comprobados en Switch; 23 pygame_sdl2 y 43 Ren’Py |
| Arranque completo | Llegó a selección de idioma y entrada de nombre según prueba del usuario |
| Perfil Lite | Registro confirma drawable 1280×720 y swap interval 2; no prueba FPS sostenidos |
| Caché | Recursos comunes escribibles en SD; una carga posterior de scripts bajó de ~62 a ~10,5 s; no es un benchmark controlado |
| Entrada | Táctil funciona según usuario. Mando detectado, pero los botones no respondían; corrección `631845b` pendiente de prueba |
| Confirmar nombre | Cierre nativo en callback PNG; corrección `631845b` instalada, pendiente de prueba |
| Guardar/cargar | No validado de extremo a extremo en este motor |
| Audio/vídeo | No hay validación suficiente de estabilidad o fluidez en Agent17 |
| NSP | No se ha generado un NSP de Agent17; se trabaja con NRO nativo |
| URM | Atajo condicional configurado; menú y funciones no confirmados en Agent17 |

### Correcciones y secuencia

1. PyConfig con rutas explícitas conserva los `:` de `romfs:/`; zlib y módulos
   estándar estáticos permiten cargar los ZIP. Entropía mediante `csrng` de libnx.
2. NACP junto a RomFS evita que elf2nro omita los datos del NRO. `verify_nro.py`
   comprueba el árbol embebido y hashes: 279 archivos en los lanzadores actuales.
3. Importador de módulos nativos con nombres de paquete; adaptación de
   platform/subprocess sin simular ejecución de procesos externos.
4. Lanzador `switch_launcher`, callbacks serializables y BLAKE2/SHA3 completaron
   el arranque que antes fallaba en Backup/imports.
5. `9b3c248`, `4e06e41`, `a7a3162`: imports de subprocess, rutas absolutas de
   dispositivo y caché de scripts comunes en SD. El antiguo traceback de
   `_posixsubprocess` permanecía en SD; no era un error de los arranques nuevos.
6. `9f0bef1`: informe nativo ubicó un puntero inválido en `eh_globals_dtor+0x14`.
   Guard al invocar el destructor de excepciones; permitió llegar a la interfaz.
   Es una mitigación y no explica toda la corrupción de TLS.
7. `56f55fd`: perfil 720p/30 FPS, gatillos mantenidos y atajo URM opcional.
8. `631845b`: informe `01790454825_0197bb45716e0000.log` ubica el cierre en
   `take_gil` / `PyGILState_Ensure`, llamado por escritura PNG desde un hilo
   Python. Se aisló TSS de CPython con mapa por clave/hilo protegido por mutex.
   También se habilitaron eventos SDL del mando sin depender del foco de
   teclado de escritorio, con registro limitado a 32 eventos sin repetición.

### Última entrega antes de integrar main

- Commit: `631845b`.
- [CI 36270176515: completada](https://github.com/Pamsho09/RenpySwitch/actions/runs/36270176515).
- NRO instalado por DBI, descargado de vuelta y comparado por SHA-256:
  `db76188cce4575091fbd81fec6c84ba611a734d825013f6093c9413edf5fb5a3`.
- Pruebas locales: ocho hilos y 10.000 ciclos por hilo; claves independientes,
  borrado/recreación y limpieza de entradas. Verificación del ELF de las cuatro
  funciones TSS y de los 279 archivos RomFS. Prueba de restauración del foco
  tras despachar un evento de mando.
- **Falta prueba en Switch:** botones, confirmar nombre, autoguardado,
  guardado/carga manual, audio y vídeos. Las pruebas locales no sustituyen esto.

## Ren’Py 7

Se conservan y se integran las correcciones de InputValue, errores de logs,
crecimiento del área de guardado, pantalla de carga, atajo URM y omisión con
gatillos. También el TLS genérico de SDL, guard de salida de hilos y guard del
destructor C++, descarte de cuadros de vídeo atrasados y límite de dos hilos
para vídeo / uno para audio. Estos límites son del motor 7; no se atribuyen al 8.

Pruebas históricas consiguieron audio, reproducción parcial y guardado/carga
con un override de SD específico del proyecto. Otras escenas siguieron
mostrando cierres y problemas de fluidez. Los vídeos reducidos y overrides
privados no se incluyen aquí. [Detalles históricos](docs/RENPY7_HISTORY.md).

## Próxima prueba

1. Ejecutar la versión instalada; probar cruceta, selección, retroceso y táctil.
2. Confirmar nombre; comprobar si el juego continúa y crea autoguardado.
3. Guardar/cargar una partida manual y comprobar la miniatura.
4. Probar música, transiciones y vídeo, anotando la escena y el comportamiento.
5. Volver a DBI/MTP y leer logs y crash report antes de modificar otra cosa.
