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

# ---------- Pantalla de bloqueo ----------
# En Plasma 6.7 vive en el paquete de la shell. Solo se cambia el reloj (LumaClock.qml, misma
# interfaz que el de Breeze): la autenticación no se toca. Si Plasma cambia la estructura,
# se deja el reloj de Breeze. Si algo fallase, kscreenlocker usa su tema de respaldo.
rpm -q plasma-workspace kscreenlocker plasma-desktop || true
LOCK=/usr/share/plasma/shells/org.kde.plasma.desktop/contents/lockscreen
if [[ -f "${LOCK}/LockScreenUi.qml" ]] && [[ "$(grep -cE '^\s*Clock \{' "${LOCK}/LockScreenUi.qml")" == 1 ]]; then
    cp /usr/share/luma/lockscreen/LumaClock.qml "${LOCK}/LumaClock.qml"
    sed -i -E 's/^(\s*)Clock \{/\1LumaClock {/' "${LOCK}/LockScreenUi.qml"
    if [[ -f "${LOCK}/qmldir" ]]; then
        echo "LumaClock 1.0 LumaClock.qml" >> "${LOCK}/qmldir"
    fi
    echo "Pantalla de bloqueo: reloj de Luma aplicado"
else
    echo "Aviso: estructura de LockScreenUi.qml desconocida; se mantiene el reloj de Breeze"
fi

# ---------- Arranque (Plymouth) ----------
SPINNER=/usr/share/plymouth/themes/spinner
python3 /ctx/tools/render_boot.py "${SPINNER}/watermark.png"
cat "${SPINNER}/spinner.plymouth" || true
# Marca centrada (la ruedita de carga queda debajo)
sed -i 's/^WatermarkVerticalAlignment=.*/WatermarkVerticalAlignment=.45/' "${SPINNER}/spinner.plymouth"
# La base usa «bgrt» (logo del fabricante en el centro); Luma usa «spinner» con su propia marca
mkdir -p /etc/plymouth
printf '[Daemon]\nTheme=spinner\n' > /etc/plymouth/plymouthd.conf
grep -i '^Theme' /etc/plymouth/plymouthd.conf /usr/share/plymouth/plymouthd.defaults 2>/dev/null || true

# Mismo comando que usa Bazzite (build_files/build-initramfs) para no cambiar nada más del arranque
QUALIFIED_KERNEL="$(dnf5 repoquery --installed --queryformat='%{evr}.%{arch}' kernel | tail -n1)"
/usr/bin/dracut --no-hostonly --kver "${QUALIFIED_KERNEL}" --reproducible --zstd -v --add ostree --add fido2 \
    -f "/usr/lib/modules/${QUALIFIED_KERNEL}/initramfs.img"
chmod 0600 "/usr/lib/modules/${QUALIFIED_KERNEL}/initramfs.img"
