# JavaScript Structure

```
/static/res/javascript/
├── core/
│   ├── api.js           // Clase API centralizada
│   ├── utils.js         // Funciones utilitarias compartidas
│   └── ui.js            // Componentes de UI reutilizables (alertas, loaders)
├── features/
│   ├── forum.js         // Toda la funcionalidad del foro (listado y detalles) 
│   ├── comments.js      // Gestión de comentarios
│   └── interactions.js  // Sistema de interacciones (likes, compartir)
└── pages/
    ├── forum-page.js    // Controlador para la página principal del foro
    └── post-page.js     // Controlador para la página de detalle del post
```