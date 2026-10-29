# Tablero Stormberg + Granite

Tablero de medios y ventas de Brooklyn Biltong, Beg & Barker, Ayoba y Granite.
Publicado en https://claude.ai/artifact/1Q7EWkaMXAbq3F9U5YX88e (corte al 27-oct-2026).

- `index.html`: página del tablero (usa el runtime `dash` del artifact; lee los datasets por id).
- `docs/index.json`: la misma página como `{text}` para `files/index.html` del store.
- `datos/*.json`: un archivo por dataset (`campanas`, `tienda`, `acciones`, `alertas`, `semaforo`, …).
- `export/tablero_stormberg_2026-10-27.html`: versión autocontenida (d3 y datos embebidos), abre sin conexión.
- `scripts/build.py`: reconstruye `campanas`, `tienda`, `bk_diario` y `promo_diario`.
  Ejecutar desde esta carpeta: `python3 -I scripts/build.py 2026-10-27 <carpeta_hojas> scripts/meta27.json`.
  `<carpeta_hojas>` debe tener `brooklyn.xlsx`, `begbarker.xlsx`, `ayoba.xlsx` y `granite.xlsx`
  exportados de las hojas de Drive (no se incluyen en el repo).
  El JSON de Meta es `{marca: [[nombre, estado, gasto, impr, clics, compras, valor], …]}`.
- `scripts/export_test.js`: prueba de la exportación con Playwright.
- `scripts/build_nov.py`: genera el media plan de Granite de noviembre desde el de octubre.

## Apps Script (web app con link)

`apps_script/` es un proyecto de Apps Script listo para publicar como aplicación web:
`Code.gs` sirve `Index.html` (la exportación autocontenida) y `appsscript.json` deja el acceso en `MYSELF`
(cámbialo a `DOMAIN` o `ANYONE` si lo vas a compartir).

Con clasp (desde esta carpeta, con tu cuenta de Google):

    npm i -g @google/clasp && clasp login
    clasp create --type webapp --title "Tablero Stormberg + Granite" --rootDir apps_script
    clasp push -f
    clasp deploy --description "Corte 27-oct"

El link queda en `https://script.google.com/macros/s/<deploymentId>/exec`.
Sin clasp: script.new → pegar `Code.gs`, crear el archivo HTML `Index` y pegar `Index.html`,
luego Implementar → Nueva implementación → Aplicación web.
Para actualizar el corte: regenerar `export/`, copiarlo a `apps_script/Index.html`, `clasp push -f`
y `clasp deploy -i <deploymentId>` (mantiene el mismo link).
