#!/usr/bin/env bash
# Paquetes añadidos sobre Bazzite. Bazzite ya trae Steam, Lutris, Gamescope,
# MangoHud, GameMode, drivers y códecs; aquí solo va lo que Luma añade o quita.
set -ouex pipefail

INSTALL=(
    # Utilidades usadas por los scripts de Luma
    jq
    pciutils
    libnotify
    # Personalización del escritorio (Fase 3 — Luma Glass)
    kvantum
)

REMOVE=(
)

dnf5 install -y --setopt=install_weak_deps=False "${INSTALL[@]}"

if ((${#REMOVE[@]})); then
    dnf5 remove -y "${REMOVE[@]}"
fi
