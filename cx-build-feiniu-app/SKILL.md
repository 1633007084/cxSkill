---
name: cx-build-feiniu-app
description: Package AthTekIPMACScanner and similar Feiniu/fnOS NAS apps into installable .fpk packages. Use when the user asks to build, package, update, or troubleshoot a 飞牛, Feiniu, fnOS, fnpack, or .fpk application, especially projects with a feiniu-product directory, manifest, cmd lifecycle scripts, app/www frontend assets, and app/server backend binaries.
---

# Build Feiniu App

## Overview

Use this skill to package the AthTekIPMACScanner project, or a similar Feiniu NAS app, into an installable `.fpk` file. Prefer the bundled script because it preserves the expected Feiniu layout and avoids accidentally building the backend for the wrong platform.

## 使用方法

中文技能名：`打包飞牛应用技能`。

后续用户只需要给项目文件夹地址即可。项目目录需要包含 `backend/`、`frontend/`、`feiniu-product/` 三个目录。

可以这样叫：

- `用打包飞牛应用技能，把 /Users/wangpeijian/Desktop/grkf/AthTekIPMACScanner 打包成飞牛应用。`
- `打包飞牛应用，项目地址是 /Users/wangpeijian/Desktop/grkf/HomeAlbum。`
- `根据这个地址生成 fpk：/Users/wangpeijian/Desktop/grkf/DeviceHealth。`
- `Use $cx-build-feiniu-app to package /Users/wangpeijian/Desktop/grkf/AthTekIPMACScanner into a Feiniu .fpk.`

执行时先读取项目里的 `feiniu-product/manifest` 判断应用名和架构，再构建后端、构建前端、同步到 `feiniu-product`，最后用 `fnpack` 生成 `.fpk`。

脚本示例：

```bash
scripts/package_feiniu_app.sh --project /Users/wangpeijian/Desktop/grkf/AthTekIPMACScanner
```

如果当前环境不能联网，且 `frontend/node_modules` 已存在，可以跳过依赖安装：

```bash
scripts/package_feiniu_app.sh --project /Users/wangpeijian/Desktop/grkf/AthTekIPMACScanner --skip-npm-install
```

如果项目里的 `feiniu-product/` 没有 `fnpack-*`，但用户提供了打包工具路径：

```bash
scripts/package_feiniu_app.sh --project /path/to/project --fnpack /path/to/fnpack
```

## Quick Start

Run the helper script from this skill:

```bash
scripts/package_feiniu_app.sh --project /Users/wangpeijian/Desktop/grkf/AthTekIPMACScanner
```

If the project already has frontend dependencies installed, the script only runs `npm install` when `frontend/node_modules` is missing. To avoid dependency installation entirely:

```bash
scripts/package_feiniu_app.sh --project /Users/wangpeijian/Desktop/grkf/AthTekIPMACScanner --skip-npm-install
```

## Project Contract

For `AthTekIPMACScanner`, keep these details aligned:

- Project root: `/Users/wangpeijian/Desktop/grkf/AthTekIPMACScanner`
- Feiniu package skeleton: `feiniu-product/`
- Backend source: `backend/cmd/server`
- Backend package target: `feiniu-product/app/server/server`
- Frontend source: `frontend/`
- Frontend package target: `feiniu-product/app/www/`
- Desktop UI config: `feiniu-product/app/ui/config`
- Default app port: `9381`
- Current manifest app name: `athtek-ipmac-scanner`
- Current manifest architecture: `x86_64`, so build Go as `GOOS=linux GOARCH=amd64 CGO_ENABLED=0`
- Packager: use `feiniu-product/fnpack-*` when present, otherwise use `fnpack` from `PATH`

## Workflow

1. Check local context first. Read `feiniu-product/manifest`, `feiniu-product/app/ui/config`, and `frontend/package.json`; inspect `git status --short` without reverting user changes.
2. Build the backend for Linux, not for the local macOS host. For `arch = x86_64`, the output binary should be an ELF x86-64 executable.
3. Build the frontend with `npm run build`, then replace only generated files under `feiniu-product/app/www/` with `frontend/dist/`.
4. Ensure lifecycle scripts and launch files are executable: `feiniu-product/cmd/*`, `feiniu-product/app/ui/index.cgi`, and `feiniu-product/app/server/server`.
5. Run `fnpack build -d feiniu-product` from the package skeleton and report the resulting `.fpk` path.
6. Validate the package enough to catch common mistakes: confirm `app/www/index.html` exists, `app/server/server` is executable, and the `.fpk` file was regenerated.

## Manual Fallback

If the helper script needs to be adapted manually, use this command sequence from the project root:

```bash
cd backend
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o ../feiniu-product/app/server/server ./cmd/server

cd ../frontend
npm install
npm run build

cd ..
rm -rf feiniu-product/app/www/*
cp -R frontend/dist/. feiniu-product/app/www/
chmod +x feiniu-product/cmd/* feiniu-product/app/ui/index.cgi feiniu-product/app/server/server
cd feiniu-product
./fnpack-1.2.1-darwin-arm64 build -d .
```

Use `--skip-npm-install` in the helper, or skip `npm install` manually, when dependencies are already present and network access is unavailable.

## Troubleshooting

- If Feiniu refuses to start the app, inspect `feiniu-product/cmd/main` and `install_callback`; they set `ATH_SCAN_ADDR`, `ATH_SCAN_DATA_DIR`, and `ATH_SCAN_WWW_DIR`.
- If the browser shows a blank page, confirm `feiniu-product/app/www/index.html` and its `assets/` files came from the latest `frontend/dist/`.
- If the backend binary says `Mach-O` on macOS, it was built for the wrong OS; rebuild with `GOOS=linux`.
- If the backend binary says `arm64` while `manifest` says `x86_64`, rebuild with `GOARCH=amd64` or update the manifest and target device architecture intentionally.
- If `fnpack` is missing, ask the user for the Feiniu packager binary or install/use a `fnpack` command available on `PATH`.
