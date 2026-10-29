# Luma Glass: lenguaje de diseño de Luma OS

Referencia visual para todo lo que se dibuje en Luma: escritorio, apps propias, instalador y web.
Está inspirado en las referencias que dio el proyecto (cristal esmerilado, píldoras con brillo de color, controles flotantes). Luma tiene su propia identidad: **no copiamos marcas, logos ni fondos de otros proyectos**.

## Principios

1. **Dos cristales, dos funciones.** El sistema (barra, bloqueo, avisos) usa *cristal oscuro*. Las ventanas y el contenido usan *cristal claro*. Así se sabe siempre qué es sistema y qué es app.
2. **El color se gana.** La interfaz es neutra. El color aparece solo cuando algo está *vivo*: música sonando, un temporizador, una grabación, «No molestar». Aparece como un brillo que sube desde el borde inferior de una píldora.
3. **Todo es redondo y flota.** No hay esquinas vivas ni barras pegadas al borde. Los controles se agrupan en píldoras.
4. **Movimiento con física.** Las cosas aparecen con escala y desenfoque, nunca de golpe, y rebotan muy poco.
5. **Grande y legible.** La tipografía es generosa, los objetivos táctiles son amplios y el cursor es grande. Pensado para cualquier persona.

## Tokens

### Color

| Token | Valor | Uso |
|---|---|---|
| `ink` | `#14161C` | Texto principal sobre claro, iconos de controles |
| `ink-2` | `#6B7080` | Texto secundario sobre claro |
| `ink-3` | `#A3A8B5` | Texto terciario, marcadores de posición |
| `paper` | `#F7F8FB` | Base del cristal claro |
| `night` | `#14171F` | Base del cristal oscuro |
| `line-light` | `rgba(255,255,255,0.55)` | Bisel del cristal claro |
| `line-dark` | `rgba(255,255,255,0.10)` | Borde del cristal oscuro |
| `accent` | `#2F7BFF` | Acento por defecto (azul Luma). El usuario puede elegir otro |
| `live-blue` | `#1E5BFF` | Píldora viva: temporizador, descargas |
| `live-red` | `#E5323B` | Píldora viva: grabación, «No molestar» |
| `live-amber` | `#F5A524` | Progreso de medios, avisos |
| `live-green` | `#21C07A` | Correcto, conectado |

Acentos seleccionables: azul `#2F7BFF`, cian `#14B8E6`, violeta `#8B5CF6`, rosa `#F0457A`, ámbar `#F5A524` y verde `#21C07A`.

### Materiales

**Cristal oscuro** (barra, bloqueo, OSD, menús del sistema)
- Fondo `night` al 62 % de opacidad, con un desenfoque de 24 px detrás.
- Borde de 1 px `line-dark` y una línea de luz de 1 px en el borde superior (`rgba(255,255,255,0.18)`).

**Cristal claro** (ventanas, diálogos, tarjetas)
- Fondo `paper` al 78 % de opacidad, con un desenfoque de 40 px. El color del fondo de pantalla tiñe la ventana, como en la referencia del reproductor.
- **Bisel grueso:** 5 px de `line-light` por dentro y 1 px de `rgba(0,0,0,0.10)` por fuera.
- Sombra: `0 24px 60px rgba(10,14,30,0.28)`.

**Píldora viva**
- Base `night`, degradado vertical del color vivo: 10 % arriba y 70 % abajo.
- Borde de 1 px del color vivo al 55 %. Texto e icono blancos.
- La píldora de medios toma el color dominante de la carátula.

### Forma

| Token | Valor |
|---|---|
| `radius-window` | 28 px |
| `radius-card` | 20 px |
| `radius-icon` | 22 % del lado (squircle) |
| `radius-pill` | altura / 2 |
| `bar-height` | 52 px (flotante, 10 px de margen al borde) |
| `pill-height` | 38 px en la barra, 44 px en apps |

### Tipografía

**DM Sans** (licencia OFL, incluida en la imagen) para toda la interfaz.

| Estilo | Tamaño / peso |
|---|---|
| Display | 40 / 700, interletrado −1 % |
| Título | 28 / 700 |
| Título de ventana | 17 / 600 |
| Cuerpo | 15 / 400 |
| Etiqueta | 14 / 500 |
| Reloj de bloqueo | 96 / 300 |

### Movimiento

| Evento | Animación |
|---|---|
| Abrir ventana | escala 0,92 → 1, opacidad 0 → 1, desenfoque 16 → 0 px; 260 ms, curva *spring* suave |
| Cerrar ventana | escala 1 → 0,96, opacidad → 0; 160 ms |
| Píldora viva aparece | crece desde un punto en la barra con rebote corto; 320 ms |
| Hover | escala 1,03; 150 ms |
| Pulsar | escala 0,96; 120 ms |
| Cambio de página | desplazamiento de 40 px + fundido; 380 ms, *ease-out cubic* |

## Componentes del sistema

### Barra Luma (inferior, flotante)
Una única barra de cristal oscuro flotando sobre el borde inferior:
- **Izquierda:** botón con el logo de Luma (abre el lanzador), separador fino y apps ancladas o abiertas como iconos squircle a color, sin fondo.
- **Centro:** *píldoras vivas* (lo que está pasando ahora): música con carátula, temporizador, grabación de pantalla, descargas. Solo aparecen cuando hay algo activo.
- **Derecha:** píldora «No molestar» (roja cuando está activa) y una píldora con borde que agrupa wifi, volumen y batería. Después, fecha y hora en texto plano.

### Controles de ventana
- Barra de título transparente, integrada en el cristal claro. El título va centrado en 17/600.
- **Izquierda:** acciones de la app en botones circulares blancos de 34 px.
- **Derecha:** una píldora blanca que agrupa minimizar, maximizar y cerrar, con iconos `ink` de trazo grueso. Si una acción no está disponible, su icono baja al 35 %.

### Botones
- **Primario:** píldora viva con el color de acento (base oscura con brillo de acento).
- **Secundario:** píldora blanca, borde 1 px `rgba(0,0,0,0.08)` y sombra suave.
- **Enlace:** texto `ink-2` subrayado con icono delante (como «Ver archivo de origen»).

### Controles
- **Deslizador:** pista gris `#C9CCD4` de 6 px, parte recorrida en ámbar o acento y mando blanco con anillo de color.
- **Interruptor:** píldora de 46×26 y mando blanco que se desliza con rebote.
- **Campo de contraseña:** píldora de cristal oscuro con puntos grandes y botón de ojo a la derecha.

### Cursor
Cursor propio **«Luma Pointer»**: flecha grande y redondeada, relleno blanco, contorno negro de 3 px con esquinas redondas y sombra suave. Tamaño por defecto 32 px.

### Pantalla de bloqueo
- Reloj enorme y fino arriba a la izquierda, con la fecha encima en `ink-3`.
- En el centro, avatar circular, nombre en 28/600 y campo de contraseña en píldora de cristal oscuro.
- El fondo de pantalla se ve sin oscurecer.

### Fondos de pantalla
Minimalistas, abstractos y propios de Luma, construidos con la geometría de la estrella. El fondo por defecto es **«Destello»**: una estrella de Luma gigante recortada por el borde y rellena de luz, con un resplandor difuminado y una estrella pequeña y nítida que la acompaña. Tiene mucho espacio vacío para que la barra y las ventanas respiren.
- **Claro:** azul sobre blanco cálido (`#F6F4F0`).
- **Oscuro:** luz cálida de naranja a magenta sobre negro (`#07080D`).

Se generan en el build (`build_files/tools/render_wallpapers.py`) con grano fino para evitar bandas. Se usan en el escritorio, el inicio de sesión y la pantalla de bloqueo.

### Cursor
Punta de flecha sin tallo con muesca en la base, esquinas muy redondeadas, contorno negro grueso, relleno blanco y sombra difuminada. La mano, el texto y los cursores de espera usan el mismo trazo.

## Logo

**Estrella de Luma:** una estrella de cuatro puntas de lados cóncavos, con los rayos verticales más largos que los horizontales (un destello de luz) y una estrella pequeña que la acompaña arriba a la derecha.
- **Glifo** (`logo-mark.svg`): blanco, para la barra, el arranque y fondos oscuros.
- **Icono** (`logo.svg`): el glifo sobre un squircle de cristal oscuro con brillo de acento azul a violeta.
- El nombre se escribe **luma** en minúsculas, DM Sans Bold.

## Cómo se implementa en KDE Plasma (Fase 3)

| Pieza | Implementación |
|---|---|
| Cristal oscuro de la barra | Tema de Plasma (SVG) traslúcido + desenfoque de KWin |
| Barra Luma | Panel flotante de Plasma con plasmoides propios: lanzador, *Píldoras vivas* (MPRIS, temporizadores, grabación) y *Estado* agrupado |
| Cristal claro en ventanas | Tema Kvantum traslúcido + efecto de desenfoque forzado (Better Blur) para apps de Luma |
| Controles de ventana | Decoración de ventana propia (KDecoration) con botones en píldora |
| Animaciones | Efectos de KWin en QML/JS: abrir/cerrar con escala y desenfoque |
| Cursor | Tema de cursor generado desde SVG (xcursorgen) en el build |
| Bloqueo e inicio de sesión | Look-and-feel de Plasma + tema SDDM en QML |
| Apps propias (Bienvenida, Luma Center) | PySide6 + QML usando estos tokens directamente |
