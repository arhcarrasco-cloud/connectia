#!/bin/bash
# Reconstruye las apps del Mac y el espejo local del hub a partir de _hub/catalogo.json
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL="$HOME/Documents/Claude/AppHub"
DEST="$HOME/Applications/Connectia"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# espejo local: la app del Dock abre esta copia, así funciona sin internet
mkdir -p "$LOCAL/iconos"
cp "$ROOT/hub/index.html"    "$LOCAL/index.html"
cp "$ROOT/hub/manifest.json" "$LOCAL/manifest.json"
cp "$ROOT/hub/iconos/"*.png  "$LOCAL/iconos/"
mkdir -p "$LOCAL/previews"
cp "$ROOT/hub/previews/"*.jpg "$LOCAL/previews/" 2>/dev/null || true
rm -rf "$LOCAL/icons"

# .icns
ICNS="$LOCAL/icns"; rm -rf "$ICNS"; mkdir -p "$ICNS"
cd "$ROOT/hub/iconos"
for p in *.png; do
  n="${p%.png}"
  [ "$n" = "apple-touch" ] && continue
  rm -rf "/tmp/ci_$n.iconset"; mkdir -p "/tmp/ci_$n.iconset"
  for s in 16 32 64 128 256 512; do
    sips -z $s $s "$p" --out "/tmp/ci_$n.iconset/icon_${s}x${s}.png" >/dev/null 2>&1
    sips -z $((s*2)) $((s*2)) "$p" --out "/tmp/ci_$n.iconset/icon_${s}x${s}@2x.png" >/dev/null 2>&1
  done
  iconutil -c icns "/tmp/ci_$n.iconset" -o "$ICNS/$n.icns" 2>/dev/null
  rm -rf "/tmp/ci_$n.iconset"
done

# bundles
rm -rf "$DEST"; mkdir -p "$DEST"

crear () { # nombre  url  icono
  local NAME="$1" URL="$2" ICON="$3"
  local APP="$DEST/$NAME.app"
  local SLUG; SLUG=$(echo "$NAME" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-')
  mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
  cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>$NAME</string>
<key>CFBundleDisplayName</key><string>$NAME</string>
<key>CFBundleExecutable</key><string>launch</string>
<key>CFBundleIconFile</key><string>icon</string>
<key>CFBundleIdentifier</key><string>mx.connectia.hub.$SLUG</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>1.0</string>
<key>CFBundleVersion</key><string>1</string>
<key>LSMinimumSystemVersion</key><string>11.0</string>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
  printf '#!/bin/bash\nexec "%s" --app="%s"\n' "$CHROME" "$URL" > "$APP/Contents/MacOS/launch"
  chmod +x "$APP/Contents/MacOS/launch"
  [ -f "$ICNS/$ICON.icns" ] && cp "$ICNS/$ICON.icns" "$APP/Contents/Resources/icon.icns"
  touch "$APP"
}

crear "Connectia App Hub" "https://connectia.mx/hub/" "connectia"

python3 - "$ROOT/_hub/catalogo.json" <<'PY' | while IFS='|' read -r n u i; do crear "$n" "$u" "$i"; done
import json, sys
for a in json.load(open(sys.argv[1]))["apps"]:
    if a.get("app_mac"):
        print(f"{a['nombre']}|{a['url']}|{a['id']}")
PY

/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister -f "$DEST" >/dev/null 2>&1 || true
touch "$DEST"
echo "apps del Mac: $(ls "$DEST" | wc -l | tr -d ' ')"
