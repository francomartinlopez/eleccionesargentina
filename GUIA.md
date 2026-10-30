# Guía de actualización mensual — Monitor Electoral de Argentina

Sitio estático publicado con GitHub Pages desde `main`: https://francomartinlopez.github.io/eleccionesargentina/
`index.html` no se toca en la actualización mensual: todo lo que cambia está en `datos/*.js` (cada archivo es `const NOMBRE=<JSON>;`).

## Reglas editoriales
- Neutral y en español rioplatense. Cada dato nuevo con fuente (URL) y fecha. Nada inventado ni completado de memoria.
- Si una fuente no se puede abrir, no busques atajos (espejos, cachés): buscá el dato en otro medio accesible o dejalo pendiente y anotalo.
- No borres datos históricos. Solo se agregan filas o se corrigen errores documentados.

## Paso a paso
1. **Encuestas** (`datos/encuestas.js`, `const ENC=[...]`). Agregá las encuestas nacionales de intención de voto presidencial 2027 publicadas desde la última `fecha` cargada. Una fila por encuestadora, fecha y serie:
   ```json
   {"fecha":"AAAA-MM-DD","fecha_aprox":false,"encuestadora":"Nombre","muestra":1200,"serie":"candidatos|fuerzas|balotaje","valores":{"Milei":33.1,"Kicillof":30.8,"Blanco":3,"Indecisos":7},"fuente":"https://...","nota":"opcional","escenario":"opcional"}
   ```
   - `fecha`: fin del trabajo de campo (si no se conoce, la de publicación y `fecha_aprox:true`).
   - Claves de `fuerzas`: `LLA`, `Peronismo`, `PRO_JxC`, `Provincias Unidas`, `UCR`, `Izquierda`, `Otros`, `Blanco`, `Indecisos` (también se aceptan `Kirchnerismo`, `Peronismo no K`, `Oposición no peronista`, `Fuerza de gobernadores`, `Partidos provinciales`).
   - Claves de `candidatos`: apellido del candidato (`Milei`, `Kicillof`, `Massa`, `Bullrich`, `Macri`, `Villarruel`, `Grabois`, `Schiaretti`, `Cristina`, `Larreta`) o `Izquierda`, `Otros`, `Blanco`, `Indecisos`. Un candidato nuevo se agrega con su apellido.
   - `balotaje`: solo escenarios de dos candidatos (por ejemplo `{"Milei":45,"Kicillof":42,"Blanco":5,"Indecisos":8}`). Cargá todos los rivales que se midan contra Milei (Kicillof, Cristina, Massa, Bullrich…): el sitio deja elegir el rival.
   - `imagen`: imagen positiva nacional de los dirigentes (buena + muy buena), con la negativa aparte: `{"serie":"imagen","valores":{"Milei":42,"Cristina":31,"Kicillof":35},"negativa":{"Milei":55,"Cristina":62,"Kicillof":50},...}`.
   - **Cristina Fernández de Kirchner** (clave `Cristina`): cargá todos los escenarios de primera vuelta y de balotaje que la incluyan y su imagen, aunque esté detenida e inhabilitada, porque las consultoras la siguen midiendo.
   - Valores en % tal como se publicaron. Verificá cada encuesta en al menos un medio reconocido o en la encuestadora. No dupliques (misma encuestadora, fecha y serie).
2. **Índice de Confianza en el Gobierno** (`datos/icg.js`). Si la UTDT publicó el ICG de un mes que no está en `serie`, agregá `{"mes":"AAAA-MM","icg":1.95,"fuente":"URL del informe UTDT"}` (escala 0–5, dos decimales) y actualizá `actualizado`. El análisis por región y segmento (`datos/icg_detalle.js`) se recalcula solo con la base de microdatos, que Franco pasa por el chat: no lo toques.
3. **Proyección 2027**: corré `python3 scripts/proyeccion.py` desde la raíz (regenera `datos/proyeccion.js` con las encuestas y el índice nuevos).
4. **Reglas electorales** (`datos/linea_de_tiempo.js`). Revisá si cambió algo del sistema electoral nacional (PASO, Boleta Única, calendario 2027, reformas). La banda `paso` dice hoy: «Vigentes para 2027». Si se suspenden, derogan o modifican, actualizá esa banda y agregá el hito con su ley, fecha y fuente.
5. **Validá**: `python3 scripts/validar.py` (cada `datos/*.js` debe leerse y tener la forma esperada). Después levantá `python3 -m http.server` en la raíz y abrí el sitio con Playwright (`require('playwright')`, `chromium.launch()` sin opciones): sin errores de página (el de Google Fonts no cuenta) y con las secciones de encuestas, confianza y proyección con datos.
6. **Publicá**: commit «Actualización mensual AAAA-MM» y push a `main`. GitHub Pages publica solo.

## Qué no se hace en la actualización mensual
- No se cambian `index.html`, `js/`, ni los resultados históricos (`presidente.js`, `diputados.js`, `senadores.js`, `gobernadores.js`, `participacion.js`, `evolucion.js`, `congreso.js`), salvo que haya una elección nacional nueva o un error documentado.
