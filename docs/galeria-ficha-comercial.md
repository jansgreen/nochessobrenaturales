# Galería de imágenes — ficha funcional y comercial

## Descripción del producto

Módulo visual para publicar, organizar y presentar fotografías de eventos de Noches Sobrenaturales. Incluye una experiencia pública elegante y responsiva, junto con un administrador privado desde el cual el equipo puede controlar todo el contenido sin modificar código.

## 1. Galería pública

- Página independiente disponible en `/galeria/`.
- Acceso directo desde la navegación principal del sitio.
- Diseño visual alineado con la identidad de Noches Sobrenaturales.
- Encabezado editorial con contador automático de fotografías publicadas.
- Cuadrícula dinámica con composiciones de diferentes alturas.
- Adaptación automática para escritorio, tablet y móvil.
- Carga diferida de imágenes para reducir el consumo inicial de datos.
- Visualización exclusiva de fotografías marcadas como publicadas.
- Orden configurable desde el dashboard.
- Título, fecha y descripción opcional por fotografía.
- Texto alternativo por imagen para accesibilidad y lectores de pantalla.
- Estado vacío profesional cuando aún no se ha publicado contenido.

## 2. Paginación

- Doce imágenes por página en la galería pública.
- Navegación mediante botones anterior y siguiente.
- Selector numérico de páginas.
- Rango de páginas abreviado cuando existe una cantidad grande de contenido.
- Manejo seguro de números de página inválidos o fuera de rango.
- Diez registros por página en el administrador para mantener una gestión ágil.

## 3. Visor interactivo de fotografías

- Apertura de imágenes en un visor de gran formato sin abandonar la página.
- Presentación del título, fecha y descripción de la fotografía.
- Navegación hacia la imagen anterior o siguiente.
- Compatibilidad con las flechas izquierda y derecha del teclado.
- Cierre mediante botón, tecla Escape o selección del fondo exterior.
- Devolución del foco a la fotografía seleccionada al cerrar el visor.
- Enlace directo al archivo como respaldo para navegadores sin soporte de diálogo.

## 4. Administración desde el dashboard

- Acceso reservado exclusivamente a usuarios administradores.
- Tarjeta de resumen con cantidad total y cantidad publicada.
- Enlace dedicado en la navegación del panel.
- Listado administrativo con miniatura, título, posición, estado y fecha de actualización.
- Creación de nuevas fotografías.
- Edición de información y configuración.
- Reemplazo del archivo visual sin crear un registro duplicado.
- Eliminación con pantalla de confirmación y vista previa.
- Publicación u ocultamiento individual sin borrar contenido.
- Mensajes de confirmación después de cada operación.

## 5. Campos administrables

- Título de la fotografía.
- Descripción o historia breve del momento.
- Archivo de imagen.
- Texto alternativo accesible.
- Fecha opcional de la fotografía o evento.
- Posición para controlar el orden visual.
- Estado publicado u oculto.

## 6. Gestión y validación de archivos

- Soporte para JPG, JPEG, PNG y WebP.
- Límite de 8 MB por archivo.
- Validación real del contenido de imagen mediante Pillow.
- Nombres internos únicos para evitar colisiones entre archivos.
- Organización automática de archivos por año y mes.
- Eliminación física del archivo cuando se elimina su registro.
- Limpieza automática de la imagen anterior cuando se reemplaza.

## 7. Almacenamiento y despliegue

- Almacenamiento local automático durante el desarrollo.
- Integración automática con Cloudinary cuando existe `CLOUDINARY_URL`.
- Persistencia de fotografías fuera del disco temporal de Heroku.
- Entrega segura mediante HTTPS desde la CDN de Cloudinary.
- Optimización automática de formato y calidad en las URLs públicas.
- El cliente debe proporcionar su propia cuenta y credencial `CLOUDINARY_URL` para el entorno de producción.

## 8. Accesibilidad y experiencia de usuario

- Estructura semántica con encabezados, navegación y figuras.
- Etiquetas descriptivas para controles del visor y paginación.
- Texto alternativo obligatorio para cada fotografía.
- Navegación completa mediante teclado.
- Indicador de página actual para tecnologías de asistencia.
- Enlaces de respaldo cuando JavaScript no está disponible.

## 9. Arquitectura técnica

- Aplicación Django independiente llamada `gallery`.
- Modelo y migración de base de datos propios.
- Formularios Django con validación del lado del servidor.
- CRUD basado en funciones y protegido por permisos de staff.
- Selector dedicado para separar la consulta pública de la lógica de presentación.
- Backend de almacenamiento intercambiable entre sistema local y Cloudinary.
- Plantillas diferenciadas para sitio público y dashboard.
- CSS responsivo integrado con el sistema visual existente.
- JavaScript nativo, sin añadir frameworks al navegador.
- Registro adicional en Django Admin para operaciones técnicas.

## 10. Control de calidad incluido

- Pruebas de acceso para visitantes, miembros y administradores.
- Pruebas de creación, edición y eliminación.
- Prueba de eliminación física de archivos.
- Pruebas de visibilidad pública y contenido oculto.
- Pruebas de paginación.
- Comprobación de migraciones pendientes.
- Validación de JavaScript, configuración Django y archivos estáticos.

## Beneficios para presentar al cliente

- El equipo actualiza la galería sin depender de un desarrollador.
- Los recuerdos de cada evento permanecen organizados y disponibles para la comunidad.
- La publicación controlada evita mostrar material antes de su aprobación.
- El diseño fortalece la imagen profesional y emocional del ministerio.
- La navegación visual favorece el tiempo de permanencia dentro del sitio.
- La arquitectura permite ampliar el módulo posteriormente con álbumes, categorías, búsqueda o descargas.

