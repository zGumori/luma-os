# Luma OS: notas para Claude

- Distro Linux: imagen bootc sobre Bazzite (Fedora Atomic + KDE Plasma). El plan está en `docs/ROADMAP.md`.
- Todo el texto visible para el usuario y la documentación va en español.
- Las imágenes solo se construyen en GitHub Actions: la máquina de desarrollo es Windows y no tiene podman. Valida los scripts con `shellcheck` (si está disponible) y `bash -n`.
- Los cambios en la imagen van en `build_files/stages/NN-nombre.sh` (se ejecutan en orden) o como archivos en `system_files/`, que se copian a `/`.
- No cambies `ID` en `os-release`: las herramientas de Universal Blue y Fedora dependen de él.
- Los archivos deben usar finales de línea LF (lo fuerza `.gitattributes`).
