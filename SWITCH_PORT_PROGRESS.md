# Estado del port — 28 de septiembre de 2026

`main` integra los motores Ren’Py 7 y Ren’Py 8. Ambos siguen siendo experimentales.
Este documento describe el motor, sus correcciones y los límites de validación.

## Ren’Py 8

| Etapa | Resultado / evidencia |
| --- | --- |
| CPython, biblioteca estándar y 66 módulos nativos | Imports comprobados en Switch; 23 pygame_sdl2 y 43 Ren’Py |
| Arranque completo | Inicialización del motor e interfaz alcanzadas en hardware |
| Perfil Lite | Registro confirma drawable 1280×720 y swap interval 2; no prueba FPS sostenidos |
| Caché | Recursos comunes escribibles en SD con marcador de versión |
| Entrada | Eventos SDL/Ren’Py comprobados por registro; prueba completa de controles pendiente |
| TSS de Python | Estado por clave/hilo aislado de pthread TLS; validación completa pendiente |
| Guardar/cargar | No validado de extremo a extremo en este motor |
| Audio/vídeo | No hay validación suficiente de estabilidad o fluidez |
| NSP | Se trabaja con NRO nativo; empaquetado no integrado y validado |
| Extensión opcional | Atajo y hook de compatibilidad disponibles; funciones pendientes de validación |

## Correcciones del motor 8

- PyConfig con rutas explícitas conserva los `:` de `romfs:/`; zlib y módulos
  estándar estáticos permiten cargar ZIP. Entropía mediante `csrng` de libnx.
- NACP junto a RomFS evita que elf2nro omita los datos del NRO. `verify_nro.py`
  comprueba el árbol embebido y hashes.
- Importador de módulos nativos con nombres de paquete; adaptación de
  platform/subprocess que informa ENOSYS para procesos externos.
- Lanzador `switch_launcher`, callbacks serializables y BLAKE2/SHA3.
- Rutas absolutas de dispositivo y caché escribible de scripts comunes en SD.
- Guard al invocar el destructor de excepciones C++; es una mitigación y
  no explica toda la corrupción de TLS.
- TSS de CPython con mapa por clave/hilo protegido por mutex. Pruebas locales
  cubren concurrencia, claves independientes, borrado y recreación.
- TLS genérico SDL y eventos de joystick/controller habilitados explícitamente.
- Salida normal directa a hbmenu; consola de diagnóstico limitada a fallos
  anteriores a la inicialización de vídeo.
- Perfil 720p/30 FPS solicitado, gatillos mantenidos y atajo opcional.
- Callback de guardados expuesto para ajustes de extensiones.
- Metadatos de Movie consultan `_original_play`/`_play`, conservan tamaños
  explícitos y máscaras laterales. Prueba local con la definición upstream.
- DROP_VIDEO habilitado en canales de vídeo; registro limitado de cargas de
  imágenes lentas para diagnóstico. La mejora de rendimiento sigue pendiente.

Las verificaciones locales de ELF, RomFS y hashes de transferencia no
sustituyen las pruebas funcionales en consola.

## Ren’Py 7

Se conservan las correcciones de InputValue, errores de logs, crecimiento del
área de guardado, pantalla de carga, atajo opcional y omisión con gatillos.
También el TLS genérico de SDL, guard de salida de hilos y guard del destructor
C++, descarte de cuadros de vídeo atrasados y límite de dos hilos para vídeo
/ uno para audio. Estos límites son del motor 7; no se atribuyen al 8.

Las pruebas históricas no establecen estabilidad general de audio, vídeo o
TLS. [Detalles técnicos](docs/RENPY7_HISTORY.md).

## Validación pendiente

1. Probar cruceta, selección, retroceso, gatillos y táctil.
2. Confirmar entrada de texto y comprobar autoguardado.
3. Guardar/cargar manualmente y comprobar la miniatura.
4. Probar música, transiciones, vídeo y regreso a hbmenu.
5. Recoger logs e informes nativos antes de modificar la instalación.
6. Validar tamaños de vídeo y medir tiempos de carga y fluidez.
