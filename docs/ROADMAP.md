# Roadmap de Luma OS

## Fase 0: Fundamentos ← *en curso*
- [x] Containerfile con tres variantes de GPU sobre Bazzite
- [x] Build diario en GitHub Actions y publicación en GHCR
- [x] Workflow de ISO (bootc-image-builder + Anaconda)
- [x] Branding básico (`os-release`, `image-info.json`)
- [x] Detección de GPU y cambio de variante (`luma-gpu-check`, `ujust luma-switch-gpu`)
- [x] Crear el repo en GitHub (privado: github.com/zGumori/luma-os)
- [ ] Ver el primer build en verde
- [ ] Al hacer el proyecto público: hacer públicos los paquetes de GHCR y volver al build diario
- [ ] Probar la ISO en una VM y en hardware real (AMD y NVIDIA)
- [ ] Firma con cosign y política de contenedores (`/etc/containers/policy.d`) para usar `ostree-image-signed`
- [ ] Rechunk de la imagen (actualizaciones delta más pequeñas)

## Fase 1: Sistema base usable
- [ ] Ofimática y apps por defecto vía Flatpak (LibreOffice/OnlyOffice, navegador)
- [ ] App de bienvenida propia (sustituir el portal de Bazzite)
- [ ] Revisar los textos de Bazzite visibles al usuario y cambiarlos por Luma
- [ ] Atajos de teclado familiares (Win+E, Win+Shift+S, Win+Espacio)

## Fase 2: Gaming
- [ ] Perfiles automáticos por juego (GameMode + governor + MangoHud)
- [ ] Integración de ProtonDB / AreWeAntiCheatYet en la tienda
- [ ] Overlay propio (FPS, temperaturas, grabación)

## Fase 3: Diseño "Luma Glass"
- [ ] Identidad: logo, paleta, tipografía, fondos dinámicos
- [ ] Global theme de Plasma: decoración de ventanas, Kvantum, iconos, cursores, sonidos
- [ ] Dock flotante + lanzador centrado con blur y degradados
- [ ] Animaciones KWin (curvas spring), esquinas redondeadas, blur mejorado
- [ ] SDDM, Plymouth y pantalla de bloqueo coherentes
- [ ] Tema para apps GTK / libadwaita
- [ ] Modo Foco: sin blur ni animaciones con juegos a pantalla completa
- [ ] Selector de look en la bienvenida: Luma / Familiar Windows / Familiar Mac

## Fase 4: Herramientas propias
- [ ] Luma Center (Qt/QML): drivers, actualizaciones, perfiles, variantes
- [ ] Asistente de migración desde Windows

## Fase 5: Beta pública
- [ ] Matriz de pruebas de hardware
- [ ] Web, documentación y canal de comunidad
