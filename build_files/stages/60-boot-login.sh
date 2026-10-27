#!/usr/bin/env bash
# Arranque, inicio de sesión y cursor de Luma. Al final regenera el initramfs para
# que Plymouth (que vive dentro del initramfs) muestre la marca de Luma.
set -ouex pipefail

export QT_QPA_PLATFORM=offscreen

# ---------- Cursor «Luma Pointer» ----------
python3 /ctx/tools/render_cursors.py /usr/share/icons
mkdir -p /usr/share/icons/default
printf '[Icon Theme]\nInherits=LumaPointer\n' > /usr/share/icons/default/index.theme
kwriteconfig6 --file /etc/xdg/kcminputrc --group Mouse --key cursorTheme LumaPointer
kwriteconfig6 --file /etc/xdg/kcminputrc --group Mouse --key cursorSize 32

# ---------- Inicio de sesión (SDDM) ----------
# El tema está en /usr/share/sddm/themes/luma y se activa en /etc/sddm.conf.d/99-luma.conf
ls /etc/sddm.conf.d/ || true

# ---------- Arranque (Plymouth) ----------
SPINNER=/usr/share/plymouth/themes/spinner
python3 /ctx/tools/render_boot.py "${SPINNER}/watermark.png"
cat "${SPINNER}/spinner.plymouth" || true
# Marca centrada (la ruedita de carga queda debajo)
sed -i 's/^WatermarkVerticalAlignment=.*/WatermarkVerticalAlignment=.45/' "${SPINNER}/spinner.plymouth"
grep -i '^Theme' /etc/plymouth/plymouthd.conf /usr/share/plymouth/plymouthd.defaults 2>/dev/null || true

# Mismo comando que usa Bazzite (build_files/build-initramfs) para no cambiar nada más del arranque
QUALIFIED_KERNEL="$(dnf5 repoquery --installed --queryformat='%{evr}.%{arch}' kernel | tail -n1)"
/usr/bin/dracut --no-hostonly --kver "${QUALIFIED_KERNEL}" --reproducible --zstd -v --add ostree --add fido2 \
    -f "/usr/lib/modules/${QUALIFIED_KERNEL}/initramfs.img"
chmod 0600 "/usr/lib/modules/${QUALIFIED_KERNEL}/initramfs.img"
