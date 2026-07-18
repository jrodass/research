# Sitio académico profesional — Jorge Rodas Silva

## Instalación
Reemplace el contenido de la rama `main` por estos archivos, manteniendo una rama de respaldo del sitio anterior.

## Publicaciones
- La web intenta leer primero `data/publications.json`.
- Si todavía está vacío, consulta ORCID desde el navegador.
- La GitHub Action `Actualizar publicaciones` genera semanalmente el JSON local.
- Los resúmenes proceden de la descripción de ORCID o del abstract disponible en Crossref.
- El título y el botón `Ver artículo` abren el DOI o el registro académico disponible.

## Activar la primera sincronización
En GitHub vaya a `Actions` → `Actualizar publicaciones` → `Run workflow`.
También active `Settings` → `Actions` → `General` → `Workflow permissions` → `Read and write permissions`.

## Logo
El logotipo optimizado está en `assets/img/logo-jorge-rodas.webp`.
