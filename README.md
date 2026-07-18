# Jorge Rodas-Silva — sitio profesional de investigación

Sitio estático, bilingüe y accesible para GitHub Pages. La producción científica se toma de ORCID `0000-0001-6526-7740` y se enriquece con OpenAlex para autores, citas, acceso abierto e indicadores bibliométricos.

## Qué incluye

- Panel principal con 10 indicadores: publicaciones, artículos, congresos, DOI, citas, índice h, citas por publicación, índice i10, publicaciones citadas y acceso abierto.
- Catálogo incorporado directamente en el HTML, con título, autores, revista, resumen, DOI, acceso abierto, búsqueda, filtro anual y paginación.
- Las publicaciones siempre son visibles: cinco por página con JavaScript y el catálogo completo como respaldo cuando JavaScript no está disponible.
- Cuando la fuente científica no ofrece abstract, `data/summary_overrides.json` conserva una síntesis editorial bilingüe basada en el tema y registro bibliográfico del trabajo.
- Español e inglés.
- Experiencia, educación, premios, afiliaciones, fotografía y logotipo existentes.
- CV imprimible: el botón «Guardar CV en PDF» abre el diálogo de impresión del navegador.
- Actualización automática semanal mediante GitHub Actions.
- Diseño adaptable, navegación por teclado, foco visible y respeto por `prefers-reduced-motion`.

## Publicar en GitHub Pages

### Opción A — GitHub web

1. Abra `https://github.com/jrodass/research`.
2. Suba el contenido de este paquete conservando exactamente las carpetas.
3. Confirme los cambios en la rama `main`.
4. Entre a **Settings → Pages**.
5. En **Build and deployment**, elija **Deploy from a branch**.
6. Seleccione `main` y `/ (root)`; luego **Save**.
7. Espere entre uno y tres minutos y abra `https://jrodass.github.io/research/`.

### Opción B — terminal

```bash
git clone https://github.com/jrodass/research.git
cd research
# Copie aquí todos los archivos del paquete, reemplazando los existentes.
git add .
git commit -m "feat: redesign professional research profile"
git push origin main
```

## Activar la actualización científica

1. En GitHub abra **Settings → Actions → General**.
2. En **Workflow permissions**, seleccione **Read and write permissions** y guarde.
3. Abra **Actions → Sync scientific profile → Run workflow**.
4. Revise que la ejecución termine en verde.

Después de activarlo, el flujo se ejecuta cada lunes y también puede lanzarse manualmente. Modifica únicamente `data/publications.json`, `data/metrics.json`, `index.html` y `en/index.html`.

## Verificación posterior

- Confirme que ES/EN cambian correctamente.
- Busque una publicación y filtre por año.
- Recorra la página usando solo la tecla `Tab`.
- En móvil, compruebe el menú y las tarjetas.
- Pulse **Guardar CV en PDF** y seleccione “Guardar como PDF”.
- Compare el total de publicaciones con ORCID.

## Fuentes y alcance de los indicadores

ORCID es la fuente maestra del catálogo. OpenAlex enriquece las coincidencias y calcula las métricas visibles. Por ello, las cifras pueden diferir de Google Scholar o Scopus. El sitio no utiliza claves privadas ni expone credenciales.
