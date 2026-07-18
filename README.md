# Sitio académico v11 — catálogo paginado

## Comportamiento
- Las publicaciones están incorporadas directamente en el HTML.
- Se muestran cinco publicaciones por página.
- Incluye navegación Anterior / Siguiente, número de página y total de resultados.
- El buscador y el filtro por año trabajan sobre todo el catálogo.
- No se presenta al visitante ningún texto técnico sobre el proceso de sincronización.

## Actualización
La acción `Sync ORCID and rebuild site` consulta ORCID, actualiza los archivos de datos y reconstruye las fichas HTML. La paginación se aplica después en el navegador sin volver a consultar servicios externos.

## Activación
Settings → Actions → General → Workflow permissions → Read and write permissions.

Luego:
Actions → Sync ORCID and rebuild site → Run workflow.
