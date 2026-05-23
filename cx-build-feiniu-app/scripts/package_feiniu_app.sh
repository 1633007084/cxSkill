#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${FEINIU_PROJECT_DIR:-/Users/wangpeijian/Desktop/grkf/AthTekIPMACScanner}"
FNPACK_BIN="${FEINIU_FNPACK:-}"
NPM_INSTALL_MODE="auto"
RUN_FNPACK="1"
CLEAN_WWW="1"

usage() {
  cat <<'USAGE'
Usage:
  package_feiniu_app.sh [--project PATH] [--fnpack PATH] [--skip-npm-install] [--no-fnpack]

Options:
  --project PATH          Project root containing backend/, frontend/, and feiniu-product/.
  --fnpack PATH           Explicit fnpack binary to use.
  --skip-npm-install      Do not run npm install, even when node_modules is missing.
  --npm-install           Always run npm install before npm run build.
  --no-fnpack             Build/sync files but do not generate the .fpk package.
  --no-clean-www          Copy dist files without first clearing feiniu-product/app/www.
  -h, --help              Show this help.

Environment:
  FEINIU_PROJECT_DIR      Default project root.
  FEINIU_FNPACK           Default fnpack binary.
USAGE
}

log() {
  printf '\n[cx-build-feiniu-app] %s\n' "$*"
}

fail() {
  printf '\n[cx-build-feiniu-app] ERROR: %s\n' "$*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing required command: $1"
}

read_manifest_value() {
  key="$1"
  manifest="$2"
  awk -F '=' -v key="$key" '
    {
      left=$1
      gsub(/^[ \t]+|[ \t]+$/, "", left)
      if (left == key) {
        value=$2
        gsub(/^[ \t]+|[ \t]+$/, "", value)
        print value
        exit
      }
    }
  ' "$manifest"
}

find_fnpack() {
  if [ -n "$FNPACK_BIN" ]; then
    printf '%s\n' "$FNPACK_BIN"
    return
  fi

  for candidate in "$FEINIU_DIR"/fnpack-* "$PROJECT_DIR"/fnpack-*; do
    if [ -f "$candidate" ]; then
      printf '%s\n' "$candidate"
      return
    fi
  done

  if command -v fnpack >/dev/null 2>&1; then
    command -v fnpack
  fi
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project)
      [ "$#" -ge 2 ] || fail "--project requires a path"
      PROJECT_DIR="$2"
      shift 2
      ;;
    --project=*)
      PROJECT_DIR="${1#--project=}"
      shift
      ;;
    --fnpack)
      [ "$#" -ge 2 ] || fail "--fnpack requires a path"
      FNPACK_BIN="$2"
      shift 2
      ;;
    --fnpack=*)
      FNPACK_BIN="${1#--fnpack=}"
      shift
      ;;
    --skip-npm-install)
      NPM_INSTALL_MODE="never"
      shift
      ;;
    --npm-install)
      NPM_INSTALL_MODE="always"
      shift
      ;;
    --no-fnpack)
      RUN_FNPACK="0"
      shift
      ;;
    --no-clean-www)
      CLEAN_WWW="0"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Unknown argument: $1"
      ;;
  esac
done

PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
FEINIU_DIR="$PROJECT_DIR/feiniu-product"
MANIFEST="$FEINIU_DIR/manifest"
SERVER_BIN="$FEINIU_DIR/app/server/server"
WWW_DIR="$FEINIU_DIR/app/www"
DIST_DIR="$FRONTEND_DIR/dist"

[ -d "$BACKEND_DIR" ] || fail "Missing backend directory: $BACKEND_DIR"
[ -d "$FRONTEND_DIR" ] || fail "Missing frontend directory: $FRONTEND_DIR"
[ -d "$FEINIU_DIR" ] || fail "Missing feiniu-product directory: $FEINIU_DIR"
[ -f "$MANIFEST" ] || fail "Missing manifest: $MANIFEST"

need_cmd go
need_cmd npm

APP_NAME="$(read_manifest_value appname "$MANIFEST")"
APP_ARCH="$(read_manifest_value arch "$MANIFEST")"
[ -n "$APP_NAME" ] || APP_NAME="$(basename "$PROJECT_DIR")"
[ -n "$APP_ARCH" ] || APP_ARCH="x86_64"

case "$APP_ARCH" in
  x86_64|amd64)
    GOARCH_VALUE="amd64"
    ;;
  arm64|aarch64)
    GOARCH_VALUE="arm64"
    ;;
  *)
    fail "Unsupported manifest arch '$APP_ARCH'. Update the script or manifest intentionally."
    ;;
esac

log "Project: $PROJECT_DIR"
log "App: $APP_NAME, manifest arch: $APP_ARCH, Go target: linux/$GOARCH_VALUE"

mkdir -p "$(dirname "$SERVER_BIN")" "$WWW_DIR"

log "Building backend"
(
  cd "$BACKEND_DIR"
  printf '+ GOOS=linux GOARCH=%s CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o %s ./cmd/server\n' "$GOARCH_VALUE" "$SERVER_BIN"
  GOOS=linux GOARCH="$GOARCH_VALUE" CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o "$SERVER_BIN" ./cmd/server
)
chmod +x "$SERVER_BIN"

if command -v file >/dev/null 2>&1; then
  file "$SERVER_BIN"
fi

log "Building frontend"
(
  cd "$FRONTEND_DIR"
  if [ "$NPM_INSTALL_MODE" = "always" ] || { [ "$NPM_INSTALL_MODE" = "auto" ] && [ ! -d node_modules ]; }; then
    npm install
  else
    printf '+ skip npm install (%s)\n' "$NPM_INSTALL_MODE"
  fi
  npm run build
)

[ -f "$DIST_DIR/index.html" ] || fail "Frontend build did not produce $DIST_DIR/index.html"

log "Syncing frontend dist to Feiniu package"
if [ "$CLEAN_WWW" = "1" ]; then
  [ "$WWW_DIR" != "/" ] || fail "Refusing to clean root directory"
  find "$WWW_DIR" -mindepth 1 -exec rm -rf {} +
fi
cp -R "$DIST_DIR"/. "$WWW_DIR"/

log "Fixing executable permissions"
for hook in "$FEINIU_DIR"/cmd/*; do
  [ -f "$hook" ] && chmod +x "$hook"
done
[ -f "$FEINIU_DIR/app/ui/index.cgi" ] && chmod +x "$FEINIU_DIR/app/ui/index.cgi"
chmod +x "$SERVER_BIN"

if [ "$RUN_FNPACK" = "1" ]; then
  FNPACK_RESOLVED="$(find_fnpack || true)"
  [ -n "$FNPACK_RESOLVED" ] || fail "fnpack binary not found. Place fnpack-* in feiniu-product/ or pass --fnpack PATH."
  [ -f "$FNPACK_RESOLVED" ] || command -v "$FNPACK_RESOLVED" >/dev/null 2>&1 || fail "fnpack not found: $FNPACK_RESOLVED"
  chmod +x "$FNPACK_RESOLVED" 2>/dev/null || true

  log "Packaging with fnpack: $FNPACK_RESOLVED"
  (
    cd "$FEINIU_DIR"
    "$FNPACK_RESOLVED" build -d "$FEINIU_DIR"
  )

  FPK_FILE="$(ls -t "$FEINIU_DIR"/*.fpk 2>/dev/null | head -1 || true)"
  [ -n "$FPK_FILE" ] || fail "fnpack finished but no .fpk file was found in $FEINIU_DIR"
  SIZE="$(du -h "$FPK_FILE" | awk '{print $1}')"
  log "FPK ready: $FPK_FILE ($SIZE)"
else
  log "Skipped fnpack packaging because --no-fnpack was set"
fi

log "Done"
