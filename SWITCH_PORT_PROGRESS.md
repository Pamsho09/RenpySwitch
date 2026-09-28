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

## Prueba SD del 28 de septiembre

Se comprobó el NRO instalado por SHA-256: era 631845b, no una versión antigua.
El registro confirma 720p/30 FPS objetivo, pero sin pulsaciones registradas.
Informe 01790615702_0197bb45716e0000.log: ahora el cierre está en
SDL_RunThread+0x40 al limpiar TLS de un decode_thread de vídeo. No es el mismo
fallo anterior en take_gil. Se incorpora el wrapper de TLS genérico SDL a
los enlaces del motor 8; antes solo estaba en la compilación del motor 7.
También se habilitan explícitamente eventos de joystick/controller al abrir
el mando y se registran hasta 32 eventos de botón en SDL, antes de Python.
La corrección y el diagnóstico requieren nueva compilación y prueba de hardware.
La causa general de corrupción TLS sigue sin establecerse.

Entrega 6ed23eb: el job RenPy8 de CI 36458810945 terminó correctamente.
ELF verificado: SDL_RunThread/SDL_TLSSet usan los wrappers del almacenamiento
TLS genérico y Controller.init llama al wrapper que habilita eventos.
Los 279 archivos RomFS coinciden con sus entradas. NRO copiado a la SD y leído
para verificar SHA-256, conservando el anterior. Pendiente nueva prueba en Switch.

Preparación local de vídeos (28 de septiembre): los 371 WebM se convirtieron
a VP8, máximo 960×540 y 30 FPS. Se verificaron hashes y formato de los 371.
El total pasó de 351.385.272 a 76.217.138 bytes (78,3% menos); esto mide tamaño,
no rendimiento de Switch. Los metadatos preservan el tamaño virtual original
(1920×1080 para todos los vídeos inventariados). NRO cbf77a8 reempaquetado y
verificado localmente. No instalado: MTP sigue devolviendo LIBUSB_ERROR_NOT_FOUND
y la SD aún no aparece montada. Pantalla negra y rendimiento pendientes de
registros nuevos y prueba en hardware. Los assets permanecen fuera del repo.


Prueba SD siguiente: el registro de 17:45:34 UTC contiene pulsaciones SDL y
RenPy y termina con "RenPy exited normally". Informe de 18:02:20 UTC
01790618540_0197bb45716e0000.log: User Break en framebufferBegin, desde
ConsoleSwRenderer_flushAndSwap y main. Se corrigió una lectura inicial errónea
de la hora: este informe es posterior al arranque. El lanzador intentaba
mostrar la consola de diagnóstico después de SDL_Quit. Ahora la salida normal
vuelve directamente a hbmenu; fallos tras inicializar vídeo quedan en el log,
y la consola solo se usa para fallos anteriores a la inicialización de vídeo.
La SD contiene autoguardados y un slot manual; su existencia no confirma carga.
Se preparan para instalación los 371 vídeos reducidos y metadatos de tamaño.

Entrega SD completada: 40ce01b, job RenPy8 de CI 36462981873 correcto.
279 archivos RomFS verificados; NRO copiado con lectura SHA-256 confirmada y
respaldo del anterior. Los 371 vídeos VP8 reducidos y switch-video-sizes.json
se copiaron a game/ sin modificar archive.rpa ni saves/. Hashes de los 371
archivos comprobados en SD. Un slot manual y un autoguardado pasaron CRC de
ZIP y contienen cabecera PNG válida; la carga en juego sigue pendiente.
Pulsaciones SDL/RenPy comprobadas por registro. Fluidez, presentación de vídeo,
regreso a hbmenu y pantalla negra pendientes de nueva prueba en consola.


Atajo URM: la última lectura de game/ en la SD no contenía 0x52_URM.rpa.
Sin el mod, L+R+X caía en la acción normal hide_windows del botón lógico Y.
El perfil ahora consume esa combinación y muestra aviso de mod no instalado
si x52URM.Open no existe. X sin la combinación conserva su acción habitual.
Esto explica una posible pantalla oscura al probar el atajo; no demuestra
que todas las pantallas negras reportadas tengan esa causa. Pendiente instalar
este cambio y comprobarlo. El archivo del mod disponible en el proyecto local
no se copia automáticamente ni se publica en el repositorio.
