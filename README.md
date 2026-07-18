# Sitio académico v8 editorial

## Diseño
- Cormorant Garamond para títulos editoriales.
- DM Sans para lectura.
- IBM Plex Mono para metadatos.
- Paleta uniforme azul marino, azul medio, blanco y gris cálido.
- Iconografía lineal monocromática.
- Publicaciones recientes en la portada y catálogo completo debajo.

## Publicaciones
- Se leen desde `data/publications.json`.
- GitHub Actions actualiza el catálogo diariamente desde ORCID.
- El visitante no espera a ORCID, por lo que la carga es rápida.
- El DOI se usa como enlace prioritario.

## Activación
En GitHub:
Settings → Actions → General → Workflow permissions → Read and write permissions.
Después:
Actions → Sync publications → Run workflow.
