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
