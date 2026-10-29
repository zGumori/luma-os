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
        -e 's|"1": "94"|"1": "97"|' \
        -e 's|"2": "47"|"2": "94"|' \
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
# Glifo de la estrella (blanco), para la barra y fondos oscuros
cp /usr/share/luma/logo-mark.svg /usr/share/icons/hicolor/scalable/apps/luma-logo-mark.svg

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

# Logos de distribución de Bazzite y Fedora (Información del sistema, menús, instalador…):
# las versiones «white» llevan la estrella blanca y el resto el logo completo
replace_logo() {
    local file="$1" source="${LOGO_SVG}" size
    [[ "${file}" == *white* ]] && source=/usr/share/luma/logo-mark.svg
    case "${file}" in
        *.svg) cp "${source}" "${file}" ;;
        *.svgz) gzip -c "${source}" > "${file}" ;;
        *.png)
            # Mismo tamaño que el original (ancho y alto de la cabecera PNG)
            size="$(python3 -c 'import struct,sys; d=open(sys.argv[1],"rb").read(24); print(*struct.unpack(">II", d[16:24]))' "${file}")"
            rsvg-convert -a -w "${size% *}" -h "${size#* }" "${source}" -o "${file}"
            ;;
    esac
    echo "Logo sustituido: ${file}"
}
while read -r logo; do
    replace_logo "${logo}"
done < <(find /usr/share/icons/hicolor /usr/share/pixmaps /usr/share/plasma/look-and-feel \
    \( -iname 'bazzite*logo*' -o -iname 'distributor-logo*' -o -iname 'fedora*logo*' \
       -o -iname 'system-logo*' -o -iname 'steamdeck*.svg' \) \
    \( -name '*.svg' -o -name '*.svgz' -o -name '*.png' \) -type f 2>/dev/null)

gtk-update-icon-cache -f /usr/share/icons/hicolor || true

# Fondos de pantalla de Bazzite, Universal Blue y Steam Deck: en el selector solo queda Luma
# (y los de KDE). Los enlaces de /usr/share/backgrounds pasan a apuntar al fondo de Luma.
find /usr/share/wallpapers -maxdepth 1 \( -iname '*bazzite*' -o -iname 'convergence*' -o -iname 'giants*' \
    -o -iname 'ublue*' -o -iname 'VGUI*' -o -iname 'Steam Deck*' -o -iname 'steamdeck*' \) \
    -print -exec rm -rf {} +
if [[ -d /usr/share/backgrounds ]]; then
    for link in default.jxl default-dark.jxl; do
        if [[ -L "/usr/share/backgrounds/${link}" ]]; then
            rm -f "/usr/share/backgrounds/${link}"
        fi
    done
fi

# Lanzadores de Bazzite que no hacen falta en Luma (documentación y foro de Bazzite, Bold Brew)
rm -f /usr/share/applications/bazzite-documentation.desktop \
      /usr/share/applications/discourse.desktop \
      /usr/share/applications/bbrew.desktop
# Cualquier otro lanzador cuyo nombre o descripción mencione Bazzite se oculta del menú (queda
# en el log). Solo se mira Name/Comment: Steam, por ejemplo, ejecuta /usr/bin/bazzite-steam.
while read -r app; do
    if grep -q '^NoDisplay=' "${app}"; then
        sed -i 's/^NoDisplay=.*/NoDisplay=true/' "${app}"
    else
        sed -i '0,/^\[Desktop Entry\]$/s//[Desktop Entry]\nNoDisplay=true/' "${app}"
    fi
    echo "Lanzador oculto: ${app}"
done < <(grep -lisE '^(Name|GenericName|Comment)(\[[^]]*\])?=.*bazzite' /usr/share/applications/*.desktop)

# Diagnóstico: lo que aún lleva el nombre de Bazzite en /usr/share (aparece en el log del build)
find /usr/share -iname '*bazzite*' -not -path '*/ublue-os/*' -not -path '*/doc/*' -not -path '*/licenses/*' -print | head -80 || true

# Tipografía de Luma (DM Sans, en /usr/share/fonts/luma)
fc-cache -f /usr/share/fonts/luma
