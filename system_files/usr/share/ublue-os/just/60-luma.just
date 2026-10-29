# Recetas de Luma OS para `ujust`

# Muestra la versión de Luma OS, la variante instalada y la GPU detectada
[group('Luma')]
luma-info:
    #!/usr/bin/bash
    source /usr/lib/os-release
    echo "${PRETTY_NAME} (${VARIANT_ID})"
    echo "Imagen: $(jq -r '."image-ref"' /usr/share/ublue-os/image-info.json 2>/dev/null)"
    echo "Recomendada para tu GPU: $(/usr/libexec/luma/luma-gpu-check --recommend)"
    echo
    lspci -mm -d ::0300
    lspci -mm -d ::0302

# Cambia a la variante de Luma OS adecuada para tu tarjeta gráfica
[group('Luma')]
luma-switch-gpu:
    /usr/libexec/luma/luma-gpu-check --switch

# Aplica el escritorio Luma (tema, colores, fondo y Barra Luma). Reemplaza tus paneles actuales.
[group('Luma')]
luma-apply-desktop:
    #!/usr/bin/bash
    read -rp "Se reemplazarán tus paneles y el fondo actuales por los de Luma. ¿Continuar? [s/N] " answer
    if [[ "${answer,,}" == s* ]]; then
        plasma-apply-lookandfeel --apply org.luma.desktop --resetLayout
    fi

# Activa o desactiva el overlay de rendimiento de Luma (en los juegos: Mayús derecha + F12)
[group('Luma')]
luma-overlay:
    #!/usr/bin/bash
    conf="${XDG_CONFIG_HOME:-$HOME/.config}/environment.d/60-luma-mangohud.conf"
    if [[ -f "$conf" ]] && grep -q '^MANGOHUD=0' "$conf"; then
        rm -f "$conf"
        echo "Overlay de Luma activado. Cierra sesión y vuelve a entrar para aplicarlo."
    else
        mkdir -p "$(dirname "$conf")"
        printf 'MANGOHUD=0\n' > "$conf"
        echo "Overlay de Luma desactivado. Cierra sesión y vuelve a entrar para aplicarlo."
    fi

# Muestra si el Modo Juego está activo y sus últimos mensajes
[group('Luma')]
luma-gamemode:
    #!/usr/bin/bash
    if busctl --user get-property org.luma.GameMode /org/luma/GameMode org.luma.GameMode Active 2>/dev/null | grep -q true; then
        echo "Modo Juego: ACTIVO"
    else
        echo "Modo Juego: inactivo"
    fi
    echo "Juegos propios: ~/.config/luma/juegos.txt · Excluidos: ~/.config/luma/no-juegos.txt"
    echo
    journalctl --user -u luma-gamemode -n 15 --no-pager -o cat
