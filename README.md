# Sitio académico v7

## Arquitectura
- Página principal de una sola página con navegación por secciones.
- Publicaciones leídas desde `data/publications.json`, por lo que cargan rápido.
- GitHub Actions consulta ORCID al subir el proyecto y cada lunes.
- El visitante nunca espera a ORCID o Crossref.
- Experiencia, educación, premios y afiliaciones se cargan desde un JSON local.
- Versión completa en inglés en `/en/`.

## Primera sincronización
Después de subir:
1. Settings → Actions → General.
2. Workflow permissions → Read and write permissions.
3. Actions → Sync ORCID publications → Run workflow.

El workflow también se ejecuta automáticamente al hacer push a `main`.

## Métricas
Las cifras iniciales reproducen las mostradas en el sitio de referencia. Scopus, Web of Science y Google Scholar no ofrecen una API pública simple para actualización automática sin credenciales o scraping. Deben revisarse periódicamente en `data/metrics.json`.
