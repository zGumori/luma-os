# Luma OS

Distribución Linux para el día a día y, sobre todo, para jugar. Tiene un diseño cuidado con cristal, degradados y animaciones, inspirado en macOS y Windows.

Luma OS es una imagen [bootc](https://containers.github.io/bootc/) construida sobre [Bazzite](https://bazzite.gg) (Fedora Atomic + KDE Plasma). Las actualizaciones son atómicas: si algo falla, se vuelve a la versión anterior desde el menú de arranque.

## Variantes

| Imagen | GPU | Base |
|---|---|---|
| `luma` | AMD / Intel | `ghcr.io/ublue-os/bazzite:stable` |
| `luma-nvidia` | NVIDIA RTX y GTX 16xx en adelante (módulos abiertos) | `ghcr.io/ublue-os/bazzite-nvidia-open:stable` |
| `luma-nvidia-legacy` | NVIDIA GTX 9xx / 10xx | `ghcr.io/ublue-os/bazzite-nvidia:stable` |

Si instalas la variante equivocada, Luma lo detecta al iniciar sesión y ofrece cambiar con un clic (`ujust luma-switch-gpu`).

## Estructura

```
Containerfile              Definición de la imagen (BASE_IMAGE elige la variante)
build_files/build.sh       Orquestador: copia system_files y ejecuta stages/ en orden
build_files/stages/        10-packages, 20-branding, 30-desktop, 99-cleanup
system_files/              Se copia tal cual a / dentro de la imagen
disk_config/iso.toml       Configuración del instalador (Anaconda)
.github/workflows/         build.yml (imágenes, diario) y build-iso.yml (ISO, manual)
docs/ROADMAP.md            Plan de desarrollo por fases
```

## Cómo se construye

Todo se construye en GitHub Actions:

1. **Imágenes:** `build.yml` se ejecuta en cada push a `main` y cada noche. Construye las tres variantes y las publica en `ghcr.io/<usuario>/<variante>:stable`.
2. **ISO:** en *Actions → Build Luma OS ISO → Run workflow* eliges la variante. La ISO queda como artefacto descargable durante 7 días.

Para construir en local hace falta Linux con `podman`:

```bash
podman build --build-arg BASE_IMAGE=ghcr.io/ublue-os/bazzite:stable -t luma:stable .
```

## Probar en un sistema existente

El proyecto es privado de momento, así que las imágenes de GHCR también lo son. Desde cualquier Fedora Atomic o Bazzite, primero hay que autenticarse con un token de GitHub con permiso `read:packages`. Esto es necesario también para recibir actualizaciones:

```bash
sudo podman login ghcr.io --authfile /etc/ostree/auth.json
sudo bootc switch ghcr.io/zgumori/luma:stable
```

## Firma de imágenes (opcional)

Genera las claves con `cosign generate-key-pair` y guarda `cosign.key` como el secreto `SIGNING_SECRET` del repositorio. Sube `cosign.pub` a la raíz del repo. Mientras no exista ese secreto, las imágenes se publican sin firmar.
