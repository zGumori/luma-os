# Luma OS — imagen bootc basada en Bazzite (Fedora Atomic + KDE Plasma)
#
# BASE_IMAGE selecciona la variante de GPU:
#   ghcr.io/ublue-os/bazzite:stable              -> luma               (AMD / Intel)
#   ghcr.io/ublue-os/bazzite-nvidia-open:stable  -> luma-nvidia        (NVIDIA RTX / GTX 16xx en adelante)
#   ghcr.io/ublue-os/bazzite-nvidia:stable       -> luma-nvidia-legacy (NVIDIA GTX 9xx / 10xx)
ARG BASE_IMAGE=ghcr.io/ublue-os/bazzite:stable

# Contexto de build: los scripts y archivos no se copian tal cual a la imagen final
FROM scratch AS ctx
COPY build_files /
COPY system_files /system_files

FROM ${BASE_IMAGE}

ARG IMAGE_NAME=luma
ARG IMAGE_VENDOR=luma-os
ARG IMAGE_TAG=stable
ARG BASE_IMAGE

RUN --mount=type=bind,from=ctx,source=/,target=/ctx \
    --mount=type=cache,dst=/var/cache \
    --mount=type=cache,dst=/var/log \
    --mount=type=tmpfs,dst=/tmp \
    IMAGE_NAME="${IMAGE_NAME}" IMAGE_VENDOR="${IMAGE_VENDOR}" \
    IMAGE_TAG="${IMAGE_TAG}" BASE_IMAGE="${BASE_IMAGE}" \
    bash /ctx/build.sh

RUN bootc container lint
