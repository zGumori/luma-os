#!/usr/bin/env bash
# Limpieza final para que la imagen pase `bootc container lint`.
set -ouex pipefail

dnf5 clean all
rm -rf /tmp/* /var/tmp/*
