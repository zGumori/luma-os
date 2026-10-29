#!/usr/bin/env bash
# Integración de Luma en el sistema: recetas ujust y servicios.
set -ouex pipefail

# Recetas `ujust` de Luma
JUSTFILE=/usr/share/ublue-os/justfile
LUMA_JUST=/usr/share/ublue-os/just/60-luma.just
if [[ -f "${JUSTFILE}" ]] && ! grep -qF "${LUMA_JUST}" "${JUSTFILE}"; then
    echo "import \"${LUMA_JUST}\"" >> "${JUSTFILE}"
fi

chmod 0755 /usr/libexec/luma/* /usr/bin/luma-welcome

# Comprobación de GPU en cada inicio de sesión (servicio de usuario global)
systemctl --global enable luma-gpu-check.service

# Apps Flatpak por defecto en el primer arranque
systemctl enable luma-flatpak-setup.service

# Modo Juego automático (servicio de usuario + script de KWin que le avisa)
systemctl --global enable luma-gamemode.service
