# Roadmap de Luma OS

## Fase 0: Fundamentos ← *en curso*
- [x] Containerfile con tres variantes de GPU sobre Bazzite
- [x] Build diario en GitHub Actions y publicación en GHCR
- [x] Workflow de ISO (bootc-image-builder + Anaconda)
- [x] Branding básico (`os-release`, `image-info.json`)
- [x] Detección de GPU y cambio de variante (`luma-gpu-check`, `ujust luma-switch-gpu`)
- [x] Crear el repo en GitHub (privado: github.com/zGumori/luma-os)
- [x] Primer build en verde (las tres variantes, 2026-10-26)
- [ ] Al hacer el proyecto público: hacer públicos los paquetes de GHCR y volver al build diario
- [x] Generar la ISO de `luma` (5,8 GB, 2026-10-27)
- [ ] Probar la ISO en una VM (guía: `docs/PRUEBAS-VM.md`) y en hardware real (AMD y NVIDIA)
- [ ] Firma con cosign y política de contenedores (`/etc/containers/policy.d`) para usar `ostree-image-signed`
- [ ] Rechunk de la imagen (actualizaciones delta más pequeñas)

## Fase 1: Sistema base usable ← *en curso*
- [x] Instalar las apps Flatpak por defecto en el primer arranque (`luma-flatpak-setup`): la lista de Bazzite más la de Luma (LibreOffice, Mission Center, Heroic, ProtonPlus, Bottles)
- [x] App de bienvenida propia (`luma-welcome`, PySide6 + QML): GPU, apps opcionales, aspecto
- [x] Quitar el portal y los anuncios de Bazzite; MOTD, fastfetch, «Acerca de» e iconos con la marca de Luma
- [x] Atajos familiares: Win+Espacio, Win+E, Win+Shift+S, Ctrl+Shift+Esc, Ctrl+Alt+T
- [x] Logo de Luma: estrella estilizada (glifo + icono de cristal oscuro)
- [ ] Probar en VM: primer arranque, instalación de flatpaks, bienvenida y atajos
- [ ] Plymouth con el logo de Luma (requiere regenerar el initramfs)

## Fase 2: Gaming
- [ ] Perfiles automáticos por juego (GameMode + governor + MangoHud)
- [ ] Integración de ProtonDB / AreWeAntiCheatYet en la tienda
- [ ] Overlay propio (FPS, temperaturas, grabación)

## Fase 3: Diseño "Luma Glass" (ver `docs/DESIGN.md`)
- [x] Lenguaje de diseño documentado: materiales, tokens, componentes, movimiento
- [x] Identidad: logo de estrella, paleta, tipografía DM Sans
- [x] App de bienvenida con el estilo Luma Glass
- [x] Fondos de pantalla propios (claro/oscuro), generados en el build
- [x] Esquemas de color Luma Claro / Luma Oscuro
- [x] Estilo de Plasma «Luma» (cristal oscuro: barra, menús, avisos)
- [x] Tema global `org.luma.desktop` + Barra Luma flotante para usuarios nuevos (`ujust luma-apply-desktop` para los existentes)
- [x] Píldoras vivas (plasmoide `org.luma.livepills`): música con carátula y «No molestar»
- [ ] Más píldoras vivas: temporizador, grabación de pantalla, descargas; estado agrupado (wifi/volumen/batería)
- [x] Decoración de ventana Luma / Luma Oscuro (Aurorae) con controles agrupados en una píldora
- [ ] Cristal claro en el contenido de las ventanas (Kvantum + desenfoque forzado)
- [ ] Instalador (Anaconda) con la marca de Luma en lugar de la de Fedora
- [x] Arranque (Plymouth) con la marca de Luma (initramfs regenerado en el build)
- [x] Inicio de sesión (SDDM) «luma»: reloj, avatar y contraseña en píldora de cristal
- [x] Pantalla de bloqueo: reloj de Luma (LumaClock), fondo oscuro y campo de contraseña en píldora
- [x] Cursor «Luma Pointer» (flecha, mano, texto, espera y progreso animados)
- [x] Animaciones de KWin: abrir/cerrar con escala (Scale), minimizar con lámpara mágica, desenfoque más intenso
- [ ] Iconos y sonidos de Luma
- [ ] Tema para apps GTK / libadwaita
- [ ] Modo Foco: sin blur ni animaciones con juegos a pantalla completa
- [ ] Selector de look en la bienvenida: Luma / Familiar Windows / Familiar Mac

## Fase 4: Herramientas propias
- [ ] Luma Center (Qt/QML): drivers, actualizaciones, perfiles, variantes
- [ ] Asistente de migración desde Windows

## Fase 5: Beta pública
- [ ] Matriz de pruebas de hardware
- [ ] Web, documentación y canal de comunidad
