#!/usr/bin/env bash
# Identidad de Luma OS: os-release e image-info (usado por las herramientas de Universal Blue).
set -ouex pipefail

: "${IMAGE_NAME:=luma}"
: "${IMAGE_VENDOR:=luma-os}"
: "${IMAGE_TAG:=stable}"

FEDORA_VERSION="$(rpm -E %fedora)"
PRETTY="Luma OS ${FEDORA_VERSION}"

# ID se mantiene igual que la base (fedora/bazzite) para no romper herramientas que lo consultan.
OS_RELEASE=/usr/lib/os-release
sed -i \
    -e "s|^NAME=.*|NAME=\"Luma OS\"|" \
    -e "s|^PRETTY_NAME=.*|PRETTY_NAME=\"${PRETTY}\"|" \
    -e "s|^HOME_URL=.*|HOME_URL=\"https://github.com/${IMAGE_VENDOR}/luma-os\"|" \
    -e "s|^BUG_REPORT_URL=.*|BUG_REPORT_URL=\"https://github.com/${IMAGE_VENDOR}/luma-os/issues\"|" \
    -e "s|^DEFAULT_HOSTNAME=.*|DEFAULT_HOSTNAME=\"luma\"|" \
    "${OS_RELEASE}"
grep -q '^DEFAULT_HOSTNAME=' "${OS_RELEASE}" || echo 'DEFAULT_HOSTNAME="luma"' >> "${OS_RELEASE}"
sed -i '/^VARIANT_ID=/d' "${OS_RELEASE}"
echo "VARIANT_ID=${IMAGE_NAME}" >> "${OS_RELEASE}"

# image-info.json: indica a ujust / actualizaciones qué imagen está instalada
IMAGE_INFO=/usr/share/ublue-os/image-info.json
if [[ -f "${IMAGE_INFO}" ]]; then
    tmp="$(mktemp)"
    jq --arg name "${IMAGE_NAME}" \
       --arg vendor "${IMAGE_VENDOR}" \
       --arg tag "${IMAGE_TAG}" \
       '."image-name" = $name
        | ."image-vendor" = $vendor
        | ."image-tag" = $tag
        | ."image-ref" = ("ostree-unverified-registry:ghcr.io/" + $vendor + "/" + $name)' \
       "${IMAGE_INFO}" > "${tmp}"
    mv "${tmp}" "${IMAGE_INFO}"
fi
