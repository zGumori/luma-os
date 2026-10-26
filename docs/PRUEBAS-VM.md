# Probar Luma OS en una máquina virtual (Windows)

## 1. Descargar la ISO

1. Abre [Actions → Build Luma OS ISO](https://github.com/zGumori/luma-os/actions/workflows/build-iso.yml) y entra en la última ejecución en verde.
2. Abajo, en **Artifacts**, descarga `luma-iso`. Es un `.zip` grande y solo se conserva 7 días.
3. Descomprímelo. Dentro están `luma-AAAAMMDD.iso` y `SHA256SUMS`.
4. Opcional: comprueba la descarga en PowerShell con `Get-FileHash luma-*.iso` y compárala con `SHA256SUMS`.

## 2. Elegir el programa de virtualización

| Programa | Recomendación |
|---|---|
| **VMware Workstation Pro** (gratis para uso personal) | **Recomendado.** Tiene la mejor aceleración 3D para Linux, así que el desenfoque y las animaciones de KDE van fluidos. Funciona aunque tengas Hyper-V o WSL activados. |
| VirtualBox 7 | Sirve, pero la aceleración 3D es floja y KDE irá a saltos. Con Hyper-V o WSL activados va más lento. |
| Hyper-V | No se recomienda: no tiene aceleración 3D para Linux. |

> En una máquina virtual no se puede probar el rendimiento en juegos ni los drivers de NVIDIA. Eso se prueba en hardware real (Fase 5).

## 3. Crear la máquina virtual (VMware)

1. *Create a New Virtual Machine* → *Typical* → selecciona la ISO.
2. Sistema operativo invitado: **Linux → Fedora 64-bit**.
3. Disco: **64 GB** como mínimo (mejor 80 GB), en un único archivo.
4. *Customize Hardware*:
   - Memoria: **8 GB** (mínimo 6 GB).
   - Procesadores: **4 núcleos** o más.
   - Display: activa **Accelerate 3D graphics** y pon 2 GB o más de memoria gráfica.
5. *Options → Advanced → Firmware type*: **UEFI**. Secure Boot puede quedarse activado: la variante `luma` no necesita firmar módulos.

En VirtualBox: tipo *Fedora (64-bit)*, **EFI activado** (Sistema → Placa base), 8 GB de RAM, 4 CPU, controlador gráfico VMSVGA con 3D activado y 128 MB de vídeo.

## 4. Instalar

1. Arranca la máquina y elige *Install Luma OS* en el menú.
2. En el instalador:
   - **Idioma:** Español.
   - **Teclado:** Español.
   - **Destino de la instalación:** el disco virtual, con particionado automático.
   - **Usuario:** crea tu usuario y marca *Hacer administrador*.
3. Pulsa *Comenzar la instalación* y reinicia al terminar. Expulsa la ISO si vuelve a arrancar el instalador.

## 5. Después de instalar: actualizaciones

El repo es privado, así que la imagen en GHCR también lo es. Para que el sistema pueda actualizarse:

1. Crea un token en GitHub: *Settings → Developer settings → Personal access tokens (classic)*, solo con el permiso `read:packages`.
2. Abre una terminal en Luma y ejecuta:

```bash
sudo podman login ghcr.io --authfile /etc/ostree/auth.json
```

Usuario: `zGumori`. Contraseña: el token.

3. Comprueba que funciona:

```bash
sudo bootc upgrade --check
```

## 6. Qué comprobar

Apunta lo que falle (con una captura si puedes) y me lo pasas.

**Primer arranque**
- [ ] Se abre sola la **Bienvenida a Luma** al iniciar sesión.
- [ ] La ventana se ve como en el diseño: cristal claro, bisel grueso, controles en píldora y tipografía DM Sans.
- [ ] Se puede arrastrar la ventana por la barra de título, y minimizar y cerrar funcionan.
- [ ] Página *Tarjeta gráfica*: detecta la gráfica virtual (VMware SVGA) y dice «Todo en orden».
- [ ] Página *Apps*: instalar una app (por ejemplo VLC) pide la contraseña y termina con «Instalada».
- [ ] Página *Aspecto*: *Aplicar* cambia el tema claro u oscuro y el color de acento de KDE.
- [ ] Con el interruptor apagado, *Empezar* hace que no vuelva a abrirse al iniciar sesión.

**Apps por defecto** (pueden tardar unos minutos con internet)
- [ ] Aparecen Firefox, LibreOffice, Heroic, Bottles, ProtonPlus y Mission Center.
- [ ] Si faltan, revisa el registro con `journalctl -b -u luma-flatpak-setup`.

**Marca y atajos**
- [ ] Menú de aplicaciones: el icono del lanzador es la estrella de Luma.
- [ ] *Preferencias → Acerca de este sistema*: dice Luma OS y muestra su logo.
- [ ] En la terminal, `fastfetch` muestra la estrella de Luma.
- [ ] Atajos:
  - `Win+Espacio`: buscador.
  - `Win+E`: archivos.
  - `Win+Shift+S`: captura de una zona.
  - `Ctrl+Shift+Esc`: administrador de tareas.
  - `Ctrl+Alt+T`: terminal.
- [ ] `ujust luma-info` muestra la versión y la gráfica.

**Seguridad de actualizaciones**
- [ ] Reinicia y comprueba que en el menú de arranque hay una entrada anterior (aparece tras la primera actualización).
