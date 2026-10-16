#!/usr/bin/env sh
set -e

DIR="$(cd "$(dirname "${0}")" && pwd -P)"
ICONE="${DIR}/moderngl.png"

if [ ! -f "${ICONE}" ]; then
    echo "Erro: moderngl.png não encontrado em ${DIR}" >&2
    exit 1
fi

ICON_DEST="${HOME}/.local/share/icons/hicolor/512x512/apps"
mkdir -p "${ICON_DEST}"
cp "${ICONE}" "${ICON_DEST}/moderngl.png"

APPS_DIR="${HOME}/.local/share/applications"
mkdir -p "${APPS_DIR}"

cat << EOF > "${APPS_DIR}/moderngl.desktop"
[Desktop Entry]
Type=Application
Name=ModernGL
Exec=python3
Icon=${ICON_DEST}/moderngl.png
StartupWMClass=moderngl
EOF

if command -v update-desktop-database > "/dev/null" 2>&1; then
    update-desktop-database "${APPS_DIR}"
fi

if command -v gtk-update-icon-cache > "/dev/null" 2>&1; then
    gtk-update-icon-cache -f -t "${HOME}/.local/share/icons/hicolor" > "/dev/null" 2>&1 || true
fi

if command -v kbuildsycoca6 > "/dev/null" 2>&1; then
    kbuildsycoca6 --noincremental > "/dev/null" 2>&1 || true
elif command -v kbuildsycoca5 > "/dev/null" 2>&1; then
    kbuildsycoca5 --noincremental > "/dev/null" 2>&1 || true
fi

rm -rf "${HOME}/.cache/icon-cache.kcache" "${HOME}/.cache/krunner" 2>/dev/null || true

echo "Configuração concluída com sucesso:"
echo "• Ícone XDG:     ${ICON_DEST}/moderngl.png"
echo "• Desktop Entry: ${APPS_DIR}/moderngl.desktop"
