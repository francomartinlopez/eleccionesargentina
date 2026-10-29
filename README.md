# Monitor Electoral de Argentina

Todas las elecciones nacionales y de gobernadores de la Argentina, de 1853 a hoy: mapas por provincia y departamento, composición del Congreso, línea de tiempo institucional, intención de voto presidencial, Índice de Confianza en el Gobierno (UTDT) y una proyección para 2027.

Sitio estático: `index.html` + `js/libs.js` + `datos/*.js`. No necesita servidor ni compilación.

## Publicar en GitHub Pages
1. Crear el repositorio (por ejemplo `monitorelectoral`) y subir todo el contenido de esta carpeta a la rama `main`.
2. En *Settings → Pages*, elegir *Deploy from a branch*, rama `main`, carpeta `/ (root)`.
3. El sitio queda en `https://<usuario>.github.io/monitorelectoral/`.

## Datos
| Archivo | Contenido | Se actualiza |
|---|---|---|
| `datos/presidente.js` | Presidenciales 1853–2023 (nacional, provincia y departamento) | Tras cada elección |
| `datos/diputados.js` | Diputados 1912–2025 | Tras cada elección |
| `datos/senadores.js` | Senadores 2003–2025 | Tras cada elección |
| `datos/gobernadores.js` | Gobernadores 1983–2025 | Tras cada elección |
| `datos/congreso.js` | Composición de las Cámaras | Tras cada elección |
| `datos/encuestas.js` | Encuestas presidenciales 2027 | Semanal |
| `datos/icg.js` | Índice de Confianza en el Gobierno (UTDT) | Mensual |
| `datos/proyeccion.js` | Proyección 2027 (se recalcula con encuestas e índice) | Semanal |
| `datos/linea_de_tiempo.js` | Hitos institucionales | Cuando cambian las reglas (p. ej., PASO) |

## Fuentes
- DINE (Ministerio del Interior): resultados por mesa 2011–2025.
- Repositorio `azha2005/257arg` (CC BY 4.0): bases de Darío Cantón (1912–1965), Ernesto Calvo (1983–1999) y PolAr (2003–2009); geometría de departamentos (Rodríguez, CEUR-CONICET; INDEC 2022).
- Wikipedia en español (CC BY-SA 4.0): fichas y tablas de elecciones, composición de las Cámaras.
- Universidad Torcuato Di Tella: Índice de Confianza en el Gobierno.
- Encuestadoras citadas en cada fila de `datos/encuestas.js`.

## Criterios
- Tendencia izquierda / centro / derecha: criterio editorial del sitio, por políticas aplicadas (gobiernos) o plataforma (candidatos). El peronismo cambia de casillero según la etapa.
- Porcentajes: en presidente (general y balotaje) sobre votos afirmativos; en PASO y legislativas, sobre válidos con los votos en blanco.
- La proyección 2027 es una estimación con rango, no un pronóstico.

Licencia de los datos propios: CC BY 4.0. Código: MIT.

### Índice de Confianza en el Gobierno (UTDT)

- `datos/icg.js`: serie mensual oficial (planilla «Histórico ICG 2001-Presente»).
- `datos/icg_detalle.js`: luna de miel por gobierno, las cinco preguntas, regiones y segmentos. Se calcula desde los microdatos oficiales:

  ```
  python scripts/icg_detalle.py "Base_histórica_2001-presente-ICG.dta"
  python scripts/proyeccion.py
  ```

  La base de microdatos (unos 24 MB) no se sube al repositorio. Cuando la UTDT publique un mes nuevo, se descarga la base, se corren los dos comandos y se suben los archivos de `datos/`. La proyección usa el cambio de confianza de cada región desde octubre de 2025 para corregir el voto de La Libertad Avanza por región; el total nacional no cambia.

### Vista previa al compartir (WhatsApp, X, Facebook, LinkedIn)

`og.png` (1200 × 630) es la imagen que aparece al compartir el enlace, y `favicon.svg` el ícono de la pestaña. Las etiquetas están en el `<head>` de `index.html` y apuntan a `https://francomartinlopez.github.io/eleccionesargentina/`. Si el repositorio tiene otro nombre, reemplazá esa dirección en las cuatro etiquetas (`og:url`, `og:image`, `twitter:image` y `canonical`). WhatsApp guarda la vista previa en caché: si la cambiás, puede tardar en actualizarse.
