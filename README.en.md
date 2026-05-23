# cxSkill

[中文](README.md) | English

`cxSkill` is a collection of skill plugins for Codex and AI coding assistants. It turns common development workflows into reusable, callable, and extensible automation capabilities.

The current plugins focus on Feiniu NAS / fnOS app development and skill marketplace metadata generation. More plugins will be added later.

Official website: [https://www.cxclaw.cn](https://www.cxclaw.cn)

## Plugins

### 1. Initialize Feiniu Project

- Plugin directory: `cx-init-feiniu-project`
- Plugin ID: `cx-init-feiniu-project`
- Chinese name: 初始化飞牛项目技能
- Purpose: initialize a Feiniu NAS / fnOS web app project from a target folder and Chinese product name.
- Generated project: Go + Gin + SQLite backend, Vue 3 + Vite + TypeScript frontend, and a `feiniu-product` package skeleton.

Use this plugin when starting a new Feiniu app from scratch:

```text
用初始化飞牛项目技能，在 /Users/wangpeijian/Desktop/grkf/HomeAlbum 创建一个项目，产品名叫 家庭相册管家。
```

You can also call the plugin ID directly:

```text
Use $cx-init-feiniu-project to create a Feiniu app at /Users/wangpeijian/Desktop/grkf/HomeAlbum with Chinese product name 家庭相册管家.
```

Script example:

```bash
cx-init-feiniu-project/scripts/init_feiniu_project.py \
  --target /Users/wangpeijian/Desktop/grkf/HomeAlbum \
  --product-cn "家庭相册管家" \
  --project-en "home-album-manager"
```

Common options:

- `--target`: target project folder.
- `--product-cn`: Chinese product name.
- `--project-en`: English project name, preferably lowercase kebab-case.
- `--port`: default backend port, `9381` by default.
- `--force`: overwrite existing directory contents, only use after confirming overwrite is intended.

### 2. Build Feiniu App

- Plugin directory: `cx-build-feiniu-app`
- Plugin ID: `cx-build-feiniu-app`
- Chinese name: 打包飞牛应用技能
- Purpose: package a compatible Feiniu NAS / fnOS app project into an installable `.fpk` file.
- Required project structure: the project root should contain `backend/`, `frontend/`, and `feiniu-product/`.

Use this plugin when you want to create a Feiniu installation package:

```text
用打包飞牛应用技能，把 /Users/wangpeijian/Desktop/grkf/AthTekIPMACScanner 打包成飞牛应用。
```

You can also call the plugin ID directly:

```text
Use $cx-build-feiniu-app to package /Users/wangpeijian/Desktop/grkf/AthTekIPMACScanner into a Feiniu .fpk.
```

Script example:

```bash
cx-build-feiniu-app/scripts/package_feiniu_app.sh \
  --project /Users/wangpeijian/Desktop/grkf/AthTekIPMACScanner
```

Common options:

- `--project`: project root.
- `--fnpack`: explicit `fnpack` binary path.
- `--skip-npm-install`: skip frontend dependency installation, useful when `node_modules` already exists or the environment is offline.
- `--npm-install`: always run `npm install`.
- `--no-fnpack`: build and sync files without generating the `.fpk` package.
- `--no-clean-www`: copy frontend build output without clearing `feiniu-product/app/www` first.

The packaging flow automatically:

- Reads `feiniu-product/manifest` to detect app name and architecture.
- Builds the Go backend for Linux.
- Builds the frontend and syncs the output to `feiniu-product/app/www/`.
- Fixes executable permissions for lifecycle scripts, UI entry, and backend binary.
- Uses `fnpack` to generate the `.fpk` package.

### 3. Skill Card JSON

- Plugin directory: `cx-skill-card-json`
- Plugin ID: `cx-skill-card-json`
- Chinese name: 技能卡片数据生成技能
- Purpose: generate marketplace-style JSON metadata from a skill name, Chinese display name, or `SKILL.md` folder.
- Output fields: `name`, `description`, `installMethod`, `badge`, and `tags`.

Use this plugin when preparing skill marketplace data:

```text
用技能卡片数据生成技能，给 figma-generate-library 生成一条 JSON。
```

You can also call the plugin ID directly:

```text
Use $cx-skill-card-json to generate JSON cards for these skill names: frontend-design, playwright.
```

Script example:

```bash
cx-skill-card-json/scripts/generate_skill_card.py frontend-design playwright
```

Example output:

```json
{
  "name": "前端设计技能",
  "description": "用于设计和优化现代 Web 页面、落地页、后台界面和组件视觉，提升排版、配色、层级、响应式和整体产品感。",
  "installMethod": "对 AI 说：“安装 frontend-design 技能。”安装后可说“用前端设计技能重新设计这个页面”。",
  "badge": "三方精选",
  "tags": ["前端设计", "UI", "视觉优化"]
}
```

## Usage

Each plugin is an independent directory. The main instruction file is `SKILL.md`, helper scripts are stored in `scripts/`, and AI assistant configuration is stored in `agents/`.

Recommended workflow:

1. Install or place the required plugin directory into your Codex / AI assistant skills directory.
2. Call the plugin by its Chinese skill name or plugin ID in conversation.
3. Provide the required parameters, such as project path, product name, or skill name.
4. The plugin will prefer its bundled scripts to reduce manual operations and avoid missing steps.

Examples:

```text
安装 cx-init-feiniu-project 技能。
```

```text
用初始化飞牛项目技能，在 /Users/wangpeijian/Desktop/grkf/DeviceHealth 创建项目，产品名叫 设备健康监控。
```

```text
用打包飞牛应用技能，打包 /Users/wangpeijian/Desktop/grkf/DeviceHealth。
```

## Directory Structure

```text
cxSkill/
├── cx-build-feiniu-app/
│   ├── SKILL.md
│   ├── agents/
│   └── scripts/
├── cx-init-feiniu-project/
│   ├── SKILL.md
│   ├── agents/
│   └── scripts/
├── cx-skill-card-json/
│   ├── SKILL.md
│   ├── agents/
│   └── scripts/
├── LICENSE
├── README.en.md
└── README.md
```

## Roadmap

This repository will continue to add more plugins, including:

- Feiniu NAS / fnOS app development tooling.
- Frontend design, page generation, and component development helpers.
- Skill marketplace metadata, installation copy, and display content generation.
- Automation for common development, packaging, testing, and release workflows.

For future plugins, use the same directory convention:

```text
plugin-name/
├── SKILL.md
├── agents/
└── scripts/
```

## License

This project is licensed under the [Apache License 2.0](LICENSE).
