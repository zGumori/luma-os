#!/usr/bin/env bash
# Sustituye la marca visible de Bazzite por la de Luma OS.
set -ouex pipefail

LOGO_SVG=/usr/share/luma/logo.svg

# Bienvenida y anuncios de Bazzite: Luma usa su propia app de bienvenida
rm -f /etc/skel/.config/autostart/bazzite-portal.desktop
rm -f /etc/xdg/autostart/bazzite-announcement.desktop

# Consejos del MOTD
rm -f /usr/share/ublue-os/motd/tips/20-bazzite.md
rm -rf /usr/share/ublue-os/motd/tips/sv

# fastfetch: logo y colores de Luma
FASTFETCH=/usr/share/ublue-os/bazzite/fastfetch.jsonc
if [[ -f "${FASTFETCH}" ]]; then
    sed -i \
        -e 's|/usr/share/ublue-os/bazzite/logo.txt|/usr/share/luma/logo.txt|' \
        -e 's|"1": "94"|"1": "96"|' \
        -e 's|"2": "47"|"2": "95"|' \
        "${FASTFETCH}"
fi

# Iconos: logo de Luma en hicolor y sustituyendo el de Bazzite (lanzador de aplicaciones)
for size in 16 22 24 32 36 48 64 96 128 256; do
    dir="/usr/share/icons/hicolor/${size}x${size}/apps"
    mkdir -p "${dir}"
    rsvg-convert -w "${size}" -h "${size}" "${LOGO_SVG}" -o "${dir}/luma-logo.png"
done
mkdir -p /usr/share/icons/hicolor/scalable/apps
cp "${LOGO_SVG}" /usr/share/icons/hicolor/scalable/apps/luma-logo.svg

# El tamaño sale del directorio "NNxNN" que contiene el icono (directo o un nivel por encima)
while read -r icon; do
    size="$(grep -oE '/[0-9]+x[0-9]+/' <<<"${icon}" | head -1 | tr -d '/')"
    size="${size%%x*}"
    if [[ -n "${size}" ]]; then
        rsvg-convert -w "${size}" -h "${size}" "${LOGO_SVG}" -o "${icon}"
    fi
done < <(find /usr/share/icons/hicolor -name 'bazzite-logo-icon.png')
while read -r icon; do
    cp "${LOGO_SVG}" "${icon}"
done < <(find /usr/share/icons/hicolor -name 'bazzite-logo-icon.svg')

gtk-update-icon-cache -f /usr/share/icons/hicolor || true
