#!/usr/bin/env bash
# Escritorio Luma Glass: fondos, tema global, estilo de Plasma y valores por defecto de KDE.
set -ouex pipefail

# Fondos de pantalla (claro/oscuro) generados en el build a partir del script
QT_QPA_PLATFORM=offscreen python3 /ctx/tools/render_wallpapers.py /usr/share/wallpapers

# Diagnóstico: configuración de Plasma que trae la imagen base (aparece en el log del build)
find /etc/xdg -maxdepth 1 \( -iname '*plasma*' -o -iname 'kdeglobals' -o -iname 'kwin*' \) -print || true
grep -rs 'LookAndFeelPackage' /etc/xdg || true

# Si la base fija su propia disposición de escritorio, la quitamos para que se use la de Luma
rm -f /etc/xdg/plasma-org.kde.plasma.desktop-appletsrc

# Valores por defecto para usuarios nuevos (/etc/xdg se lee antes que la configuración del usuario)
kw() { kwriteconfig6 --file "/etc/xdg/$1" "${@:2}"; }
kw kdeglobals --group KDE --key LookAndFeelPackage org.luma.desktop
kw kdeglobals --group General --key ColorScheme LumaLight
kw kdeglobals --group General --key AccentColor "47,123,255"
kw plasmarc --group Theme --key name luma
# Tipografía de la interfaz: DM Sans
kw kdeglobals --group General --key font "DM Sans,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
kw kdeglobals --group General --key menuFont "DM Sans,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
kw kdeglobals --group General --key toolBarFont "DM Sans,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
kw kdeglobals --group General --key smallestReadableFont "DM Sans,8,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
kw kdeglobals --group WM --key activeFont "DM Sans,10,-1,5,600,0,0,0,0,0,0,0,0,0,0,1"
# Pantalla de bloqueo con el fondo de Luma
kw kscreenlockerrc --group Greeter --group Wallpaper --group org.kde.image --group General \
    --key Image "file:///usr/share/wallpapers/Luma/"
# Decoración de ventana Luma (Aurorae) con los controles agrupados a la derecha
kw kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
kw kwinrc --group org.kde.kdecoration2 --key theme __aurorae__svg__Luma
kw kwinrc --group org.kde.kdecoration2 --key ButtonsOnLeft ""
kw kwinrc --group org.kde.kdecoration2 --key ButtonsOnRight IAX
# Desenfoque de KWin activado (lo usan la barra y los menús de cristal)
kw kwinrc --group Plugins --key blurEnabled true
kw kwinrc --group Plugins --key contrastEnabled true
kw kwinrc --group Effect-blur --key BlurStrength 12
kw kwinrc --group Effect-blur --key NoiseStrength 4

# Animaciones (docs/DESIGN.md → Movimiento)
# Abrir/cerrar ventanas: efecto «Scale» de KWin, desde 0,92 al abrir y hasta 0,96 al cerrar
kw kwinrc --group Plugins --key scaleEnabled true
kw kwinrc --group Plugins --key fadeEnabled false
kw kwinrc --group Effect-scale --key Duration 260
kw kwinrc --group Effect-scale --key InScale 0.92
kw kwinrc --group Effect-scale --key OutScale 0.96
# Minimizar: «lámpara mágica», al estilo de macOS
kw kwinrc --group Plugins --key magiclampEnabled true
kw kwinrc --group Plugins --key squashEnabled false
