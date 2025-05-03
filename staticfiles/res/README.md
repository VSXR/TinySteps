# CSS DIRECTORY STRUCTURE

```
static/res/css/
├── main.css                   # Archivo principal que importa todos los demás
├── base/                      # Estilos base y reset
│   ├── _reset.css            # Normalización y reseteo
│   ├── _typography.css       # Tipografía
│   └── _accessibility.css    # Accesibilidad
├── utils/                     # Utilidades y configuraciones
│   ├── _variables.css        # Variables CSS (colores, espaciados, etc.)
│   ├── _responsive.css       # Media queries
│   ├── _utilities.css        # Clases utilitarias
│   └── _animations.css       # Animaciones
├── layout/                    # Estructura de la página
│   ├── _grid.css             # Sistema de grid
│   └── _containers.css       # Contenedores
├── navigation/                # Componentes de navegación
│   ├── _header.css           # Estilos del header
│   ├── _main_nav.css         # Navegación principal
│   └── _mobile_nav.css       # Navegación móvil
├── components/                # Componentes reutilizables
│   ├── _buttons.css          # Botones
│   ├── _forms.css            # Formularios
│   ├── _cards.css            # Tarjetas
│   └── _modal.css            # Modales
└── pages/                     # Estilos específicos de página
    ├── _home.css             # Página de inicio
    ├── _about.css            # Página de acerca de
    └── _dashboard.css        # Dashboard
```

# JAVASCRIPT DIRECTORY STRUCTURE

```
static/res/javascript/
├── main.js                    # Archivo principal (inicialización)
├── config/                    # Configuración global
│   └── settings.js           # Ajustes globales de la aplicación
├── utils/                     # Utilidades
│   ├── helpers.js            # Funciones auxiliares
│   ├── validators.js         # Validaciones
│   └── api.js                # Manejo de peticiones AJAX
├── components/                # Componentes reutilizables
│   ├── forms.js              # Lógica de formularios
│   ├── modals.js             # Manejo de modales
│   ├── alerts.js             # Notificaciones/alertas
│   └── charts.js             # Gráficos (si aplica)
├── navigation/                # Lógica de navegación
│   ├── header.js             # Interactividad del header
│   ├── main-nav.js           # Navegación principal
│   └── mobile-nav.js         # Navegación móvil
└── pages/                     # Lógica específica de páginas
    ├── home.js               # Funcionalidad página inicio
    ├── parent_forum.js       # Foro de padres
    └── dashboard.js          # Funcionalidad del dashboard
```
