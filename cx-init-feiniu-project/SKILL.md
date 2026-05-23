---
name: cx-init-feiniu-project
description: Initialize a new Feiniu/fnOS NAS web application project using the AthTekIPMACScanner architecture. Use when the user provides a folder path and Chinese product name, asks to create/scaffold/init a 飞牛, Feiniu, fnOS, .fpk, Go backend, Vue frontend, or feiniu-product project, and wants the Chinese name converted into an appropriate English project/app identifier.
---

# Init Feiniu Project

## Overview

Use this skill to create a new project with the same architecture as `AthTekIPMACScanner`: Go backend, Vue/Vite frontend, and a `feiniu-product` package skeleton ready for Feiniu `.fpk` packaging.

## 使用方法

中文技能名：`初始化飞牛项目技能`。

后续用户可以这样叫：

- `用初始化飞牛项目技能，在 /Users/wangpeijian/Desktop/grkf/HomeAlbum 创建一个项目，产品名叫 家庭相册管家。`
- `初始化一个飞牛项目，路径是 /Users/wangpeijian/Desktop/grkf/DeviceHealth，中文名是 设备健康监控。`
- `Use $cx-init-feiniu-project to create a Feiniu app at /Users/wangpeijian/Desktop/grkf/HomeAlbum with Chinese product name 家庭相册管家.`

执行时先从中文产品名推导英文项目名，再运行脚本。示例：

```bash
scripts/init_feiniu_project.py \
  --target /Users/wangpeijian/Desktop/grkf/HomeAlbum \
  --product-cn "家庭相册管家" \
  --project-en "home-album-manager"
```

如果用户已经提供英文项目名，直接使用用户提供的英文名；如果目标目录非空，除非用户明确说覆盖，否则不要使用 `--force`。

## Required Inputs

Ask only if missing:

- Target folder path, such as `/Users/wangpeijian/Desktop/grkf/NewProduct`.
- Chinese product name, such as `星创网络扫描器`.

Derive the English project name from the Chinese product name before running the script. Prefer a clear product-style English name, then normalize it to kebab-case. Examples:

- `星创网络扫描器` -> `starlink-network-scanner` or `star-creation-network-scanner`
- `家庭相册管家` -> `home-album-manager`
- `设备健康监控` -> `device-health-monitor`

If the user gives both Chinese and English names, respect the provided English name.

## Quick Start

From this skill directory, run:

```bash
scripts/init_feiniu_project.py \
  --target /Users/wangpeijian/Desktop/grkf/NewProduct \
  --product-cn "中文产品名" \
  --project-en "english-product-name"
```

Optional flags:

```bash
scripts/init_feiniu_project.py --target PATH --product-cn "中文名" --project-en english-name --port 9381 --force
```

Use `--force` only when the user explicitly wants to overwrite files in an existing project folder. The script refuses to write into a non-empty directory by default.

## Generated Architecture

The script creates:

- `backend/`: Go module with Gin API, SQLite migrations, embedded migrations, health/bootstrap routes, and static file fallback.
- `frontend/`: Vue 3 + Vite + TypeScript app with a polished starter UI and API service.
- `feiniu-product/`: Feiniu skeleton with `manifest`, `config/resource`, `config/privilege`, `cmd/*` lifecycle scripts, `app/ui/config`, `app/ui/index.cgi`, `app/server/.gitkeep`, and `app/www/index.html`.
- Root docs and ignore files: `.gitignore`, `产品介绍.md`, and `README.md`.

## Workflow

1. Inspect the requested target path. Do not overwrite an existing non-empty directory unless the user requested it.
2. Translate or adapt the Chinese product name into an English project name. Use lowercase kebab-case for app IDs and package names.
3. Run the bundled script with `--target`, `--product-cn`, and `--project-en`.
4. If the user wants dependencies installed, run `npm install` in `frontend/` and `go mod tidy` in `backend/`.
5. For packaging, use `$cx-build-feiniu-app` after initialization.

## Naming Rules

Use these derived identifiers consistently:

- `project_slug`: lowercase kebab-case, e.g. `device-health-monitor`.
- `go_module`: same as `project_slug` unless the user provides a module path.
- `env_prefix`: uppercase snake-like prefix from the slug, e.g. `DEVICE_HEALTH_MONITOR`.
- `desktop app key`: `${project_slug}.Application`.
- `database file`: slug with hyphens converted to underscores, e.g. `device_health_monitor.db`.

## Notes

- The generated backend target port defaults to `9381`, matching the source project.
- The generated Feiniu manifest defaults to `arch = x86_64`.
- The generated lifecycle scripts set `${ENV_PREFIX}_ADDR`, `${ENV_PREFIX}_DATA_DIR`, and `${ENV_PREFIX}_WWW_DIR`.
- The generated project intentionally does not include `node_modules`, build artifacts, `.fpk` files, or copied `fnpack` binaries.
