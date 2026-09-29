# RenPySwitch

Port nativo experimental de Ren’Py para Nintendo Switch. `main` reúne el
trabajo de los motores Ren’Py 7 y Ren’Py 8.
Consulta el [estado actual](SWITCH_PORT_PROGRESS.md) para conocer sus límites.

| Perfil | Motor | Python | Salida principal |
| --- | --- | --- | --- |
| `renpy8` (predeterminado) | 8.3.7 | 3.9.21 | Lanzador NRO, ELF, pruebas y bibliotecas estáticas |
| `renpy7` | 7.6.3 | 2.7 | Árbol `switch/`, `exefs/main`, `lib.zip` y ELF comprimido |

Los scripts compilados para Python 3 necesitan el motor Ren’Py 8. Copiar un
RPA entre versiones no convierte sus scripts. El lanzador Ren’Py 8 usa una
configuración fija; aún no es un empaquetador genérico.

## Compilar desde macOS o Linux

Requisitos: Git, Docker con Compose, acceso a Internet y espacio para fuentes,
imagen del compilador y resultados. Desde este directorio:

```sh
# Ren’Py 8, resultados en artifacts/
docker compose run --build --rm build

# Ren’Py 7, resultados separados
RUNTIME=renpy7 OUTPUT_DIR=./artifacts-renpy7 docker compose run --build --rm build
```

Compose usa `devkitpro/devkita64:20230910` y `linux/amd64`. En Apple Silicon
necesita emulación: una prueba anterior del motor 7 falló en el compilador
emulado. Para compilaciones verificadas se ha usado GitHub Actions sobre
Linux x86-64. `BUILD_PLATFORM` permite cambiar la plataforma, pero no convierte
las herramientas x86 a ARM. No se garantiza una compilación local en todos los Mac.

El workflow compila ambos perfiles por separado y publica
`renpy-switch-renpy7` y `renpy-switch-renpy8`. También admite ejecución manual.
No mezcles artefactos de perfiles distintos ni ZIP de una versión con ELF
nativo incompatible. [Arquitectura, despliegue y diagnóstico](docs/DEVELOPMENT.md).

## Lanzador Ren’Py 8

Las rutas de instalación están definidas en `experimental/python3/game_entry.py`
y `experimental/python3/game_main.c`; los nombres de salida se definen en
`experimental/python3/bootstrap.sh`. Consulta esos archivos al preparar una
instalación. El motor crea `saves/`, `logs/` y `engine-common-8.3.7/` dentro de
la carpeta del lanzador. La primera preparación de caché tarda más.
Ejecuta el NRO desde hbmenu con memoria de aplicación.

Controles configurados para el perfil Lite:

- Salida solicitada de 1280×720 y objetivo de 30 FPS; resolución y swap interval
  comprobados en hardware, fluidez sostenida pendiente.
- Mantener ZL o ZR: omitir; soltar el último gatillo: detener la omisión.
- L + R + X: atajo condicional para una extensión opcional instalada por separado.
- Ren’Py 7 usa ZL/ZR para alternar la omisión, en lugar del modo mantenido del motor 8.

## Documentación

- [Estado de los motores](SWITCH_PORT_PROGRESS.md).
- [Arquitectura, compilación, DBI y diagnóstico](docs/DEVELOPMENT.md).
- [Detalles técnicos Ren’Py 8](experimental/python3/README.md).
- [Historial técnico Ren’Py 7](docs/RENPY7_HISTORY.md).

El repositorio contiene el motor y sus herramientas. Los recursos externos,
extensiones, claves de consola y paquetes NSP se suministran por separado.
Se conserva el trabajo original de knautilus.
