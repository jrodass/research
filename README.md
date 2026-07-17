# Research Site v2

Sitio académico estático para GitHub Pages.

## Publicación

1. Haz una copia de seguridad del repositorio actual.
2. Sustituye su contenido por los archivos de esta carpeta.
3. Confirma que GitHub Pages publique desde `main` y `/ (root)`.
4. Haz commit y push.
5. Abre `https://jrodass.github.io/research/`.

## Estructura

- `index.html`: portada.
- `publications.html`: publicaciones con búsqueda y filtro.
- `posts.html`: noticias y divulgación.
- `about.html`: perfil.
- `cv.html`: experiencia y formación.
- `es/index.html`: portada en español.
- `assets/css/styles.css`: diseño.
- `assets/js/app.js`: navegación y conexión con ORCID.
- `data/site.json`: datos centrales para futuras ampliaciones.

## ORCID

El sitio utiliza el ORCID `0000-0001-6526-7740`.
La API pública de ORCID puede aplicar límites temporales o bloquear ciertas solicitudes desde el navegador. Para producción robusta se recomienda añadir una GitHub Action que genere un archivo local `data/publications.json`.

## Próximas mejoras recomendadas

- Foto profesional optimizada en WebP.
- CV descargable en PDF.
- Google Scholar, Scopus y Web of Science.
- Posts individuales.
- SEO avanzado, Open Graph, sitemap y analytics.
- GitHub Action para sincronización programada de ORCID/Crossref.
