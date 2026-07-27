# Jorge Rodas-Silva — sitio profesional de investigación

Sitio estático, bilingüe y accesible para GitHub Pages. El catálogo combina ORCID `0000-0001-6526-7740` con los perfiles Scopus `59258484700` y `57188854666`; OpenAlex y Crossref completan autores, resúmenes, citas, acceso abierto e indicadores bibliométricos.

## Qué incluye

- Panel principal con 10 indicadores: publicaciones, artículos, congresos, DOI, citas, índice h, citas por publicación, índice i10, publicaciones citadas y acceso abierto.
- Sección bilingüe de líneas e intereses de investigación con seis filtros temáticos conectados al catálogo.
- Catálogo incorporado directamente en el HTML, con título, autores, revista, resumen, DOI, acceso abierto, búsqueda, filtro anual y paginación.
- Las publicaciones siempre son visibles: cinco por página con JavaScript y el catálogo completo como respaldo cuando JavaScript no está disponible.
- Cuando la fuente científica no ofrece abstract, `data/summary_overrides.json` conserva una síntesis editorial bilingüe basada en el tema y registro bibliográfico del trabajo.
- Español e inglés.
- Experiencia, educación, premios, afiliaciones, fotografía y logotipo existentes.
- CV imprimible: el botón «Guardar CV en PDF» abre el diálogo de impresión del navegador.
- Actualización automática diaria mediante GitHub Actions.
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

## Activar la actualización científica automática

### 1. Crear la clave de Scopus

1. Registre una aplicación académica en `https://dev.elsevier.com/`.
2. Copie la API key generada. No la escriba en el código ni la envíe por correo o chat.
3. Si la biblioteca de UNEMI le proporciona un *institutional token*, consérvelo para el paso siguiente. Es opcional, pero puede ampliar el acceso a metadatos y resúmenes.

### 2. Guardar las credenciales de forma segura

1. En GitHub abra el repositorio y entre a **Settings → Secrets and variables → Actions**.
2. Pulse **New repository secret**.
3. Cree `ELSEVIER_API_KEY` y pegue la API key.
4. Solo si dispone del token institucional, cree también `ELSEVIER_INSTTOKEN`.

### 3. Activar el flujo

1. En **Settings → Actions → General**, seleccione **Read and write permissions** y guarde.
2. Abra **Actions → Sync scientific profile → Run workflow**.
3. Revise que la ejecución termine en verde.

Después de activarlo, el flujo se ejecuta todos los días a las 06:17 (hora de Ecuador) y también puede lanzarse manualmente. Consulta ambos perfiles Scopus, une sus resultados con ORCID, elimina duplicados por DOI, EID o título, completa los metadatos disponibles y modifica únicamente `data/publications.json`, `data/metrics.json`, `index.html` y `en/index.html`. Si una fuente falla temporalmente, el catálogo anterior se conserva para evitar que desaparezcan publicaciones.

## Verificación posterior

- Confirme que ES/EN cambian correctamente.
- Busque una publicación y filtre por año.
- Recorra la página usando solo la tecla `Tab`.
- En móvil, compruebe el menú y las tarjetas.
- Pulse **Guardar CV en PDF** y seleccione “Guardar como PDF”.
- Compare el total y los títulos con los dos perfiles de Scopus y con ORCID.

## Fuentes y alcance de los indicadores

Scopus y ORCID son las fuentes maestras del catálogo. OpenAlex y Crossref enriquecen las coincidencias y cubren campos ausentes. Las métricas se recalculan sobre el catálogo unificado, por lo que pueden diferir de las que cada base muestra de forma aislada. La clave privada se lee únicamente desde GitHub Actions y nunca se publica en el sitio.
