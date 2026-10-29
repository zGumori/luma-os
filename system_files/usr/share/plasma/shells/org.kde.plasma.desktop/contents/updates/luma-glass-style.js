// Luma OS: activa el estilo Kvantum (cristal en las ventanas) en usuarios que ya existían
// antes de que Luma lo trajera. Se ejecuta una sola vez por usuario. Solo cambia el estilo
// de KDE por defecto (Breeze, vacío o el Kvantum de /etc/xdg): si el usuario eligió otro a
// mano, no se toca. Con el esquema oscuro de Luma se usa la variante oscura.
const globals = ConfigFile("kdeglobals", "KDE");
const style = String(globals.readEntry("widgetStyle") || "");
if (["", "breeze", "kvantum"].indexOf(style.toLowerCase()) !== -1) {
    const general = ConfigFile("kdeglobals", "General");
    const scheme = String(general.readEntry("ColorScheme") || "");
    globals.writeEntry("widgetStyle", scheme === "LumaDark" ? "kvantum-dark" : "kvantum");
}
