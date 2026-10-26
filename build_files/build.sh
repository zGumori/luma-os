#!/usr/bin/env bash
# Orquestador del build: copia los archivos de sistema y ejecuta cada etapa en orden.
set -ouex pipefail

CTX=/ctx

cp -avf "${CTX}/system_files"/. /

for stage in "${CTX}"/stages/*.sh; do
    echo "::group:: ===== $(basename "${stage}") ====="
    bash "${stage}"
    echo "::endgroup::"
done
