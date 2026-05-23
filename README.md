# cxSkill

默认中文 | [English](README.en.md)

`cxSkill` 是一组面向 Codex / AI 编程助手的技能插件集合，用来把常用开发流程沉淀成可复用、可调用、可扩展的自动化能力。

当前插件主要围绕飞牛 NAS / fnOS 应用开发与技能市场数据生成，后续会继续增加更多实用插件。

官网地址：[https://www.cxclaw.cn](https://www.cxclaw.cn)

## 插件列表

### 1. 初始化飞牛项目

- 插件目录：`cx-init-feiniu-project`
- 插件 ID：`cx-init-feiniu-project`
- 中文名称：初始化飞牛项目技能
- 作用：根据目标目录和中文产品名，自动初始化一个飞牛 NAS / fnOS Web 应用项目。
- 生成内容：Go + Gin + SQLite 后端、Vue 3 + Vite + TypeScript 前端、`feiniu-product` 飞牛应用打包骨架。

适合在需要从零创建飞牛应用时使用，例如：

```text
用初始化飞牛项目技能，在 /Users/wangpeijian/Desktop/grkf/HomeAlbum 创建一个项目，产品名叫 家庭相册管家。
```

也可以直接指定技能 ID：

```text
Use $cx-init-feiniu-project to create a Feiniu app at /Users/wangpeijian/Desktop/grkf/HomeAlbum with Chinese product name 家庭相册管家.
```

脚本调用示例：

```bash
cx-init-feiniu-project/scripts/init_feiniu_project.py \
  --target /Users/wangpeijian/Desktop/grkf/HomeAlbum \
  --product-cn "家庭相册管家" \
  --project-en "home-album-manager"
```

常用参数：

- `--target`：项目生成目录。
- `--product-cn`：中文产品名。
- `--project-en`：英文项目名，建议使用小写 kebab-case。
- `--port`：后端默认端口，默认 `9381`。
- `--force`：覆盖已有目录内容，仅在确认需要覆盖时使用。

### 2. 打包飞牛应用

- 插件目录：`cx-build-feiniu-app`
- 插件 ID：`cx-build-feiniu-app`
- 中文名称：打包飞牛应用技能
- 作用：将符合结构的飞牛 NAS / fnOS 应用项目打包成可安装的 `.fpk` 文件。
- 适用项目结构：项目根目录需要包含 `backend/`、`frontend/`、`feiniu-product/`。

适合在完成开发后生成飞牛安装包时使用，例如：

```text
用打包飞牛应用技能，把 /Users/wangpeijian/Desktop/grkf/AthTekIPMACScanner 打包成飞牛应用。
```

也可以直接指定技能 ID：

```text
Use $cx-build-feiniu-app to package /Users/wangpeijian/Desktop/grkf/AthTekIPMACScanner into a Feiniu .fpk.
```

脚本调用示例：

```bash
cx-build-feiniu-app/scripts/package_feiniu_app.sh \
  --project /Users/wangpeijian/Desktop/grkf/AthTekIPMACScanner
```

常用参数：

- `--project`：项目根目录。
- `--fnpack`：指定 `fnpack` 打包工具路径。
- `--skip-npm-install`：跳过前端依赖安装，适合 `node_modules` 已存在或离线环境。
- `--npm-install`：强制执行 `npm install`。
- `--no-fnpack`：只构建并同步文件，不生成 `.fpk`。
- `--no-clean-www`：复制前端构建产物前不清空 `feiniu-product/app/www`。

打包流程会自动完成：

- 读取 `feiniu-product/manifest` 判断应用名和架构。
- 将 Go 后端构建为 Linux 目标平台二进制。
- 执行前端构建并同步到 `feiniu-product/app/www/`。
- 修复生命周期脚本、UI 入口和后端二进制权限。
- 使用 `fnpack` 生成 `.fpk` 安装包。

### 3. 技能卡片数据生成

- 插件目录：`cx-skill-card-json`
- 插件 ID：`cx-skill-card-json`
- 中文名称：技能卡片数据生成技能
- 作用：根据技能名称、中文展示名或 `SKILL.md` 目录，生成插件市场展示用 JSON 数据。
- 输出字段：`name`、`description`、`installMethod`、`badge`、`tags`。

适合在整理插件市场数据时使用，例如：

```text
用技能卡片数据生成技能，给 figma-generate-library 生成一条 JSON。
```

也可以直接指定技能 ID：

```text
Use $cx-skill-card-json to generate JSON cards for these skill names: frontend-design, playwright.
```

脚本调用示例：

```bash
cx-skill-card-json/scripts/generate_skill_card.py frontend-design playwright
```

输出示例：

```json
{
  "name": "前端设计技能",
  "description": "用于设计和优化现代 Web 页面、落地页、后台界面和组件视觉，提升排版、配色、层级、响应式和整体产品感。",
  "installMethod": "对 AI 说：“安装 frontend-design 技能。”安装后可说“用前端设计技能重新设计这个页面”。",
  "badge": "三方精选",
  "tags": ["前端设计", "UI", "视觉优化"]
}
```

## 如何使用

每个插件都是一个独立目录，核心说明文件为 `SKILL.md`，辅助脚本放在 `scripts/` 目录下，AI 助手配置放在 `agents/` 目录下。

推荐使用方式：

1. 将需要的插件目录安装或放入你的 Codex / AI 助手技能目录。
2. 在对话中使用中文技能名或插件 ID 调用插件。
3. 根据插件提示提供必要参数，例如项目路径、产品名、技能名称等。
4. 插件会优先使用目录内脚本完成任务，减少手动操作和流程遗漏。

示例：

```text
安装 cx-init-feiniu-project 技能。
```

```text
用初始化飞牛项目技能，在 /Users/wangpeijian/Desktop/grkf/DeviceHealth 创建项目，产品名叫 设备健康监控。
```

```text
用打包飞牛应用技能，打包 /Users/wangpeijian/Desktop/grkf/DeviceHealth。
```

## 目录结构

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

## 后续计划

这个仓库会持续补充更多插件，方向包括但不限于：

- 飞牛 NAS / fnOS 应用开发工具链。
- 前端设计、页面生成与组件开发辅助。
- 插件市场数据、安装文案和展示信息生成。
- 常用开发、打包、测试、发布流程自动化。

如果后续新增插件，建议保持相同目录规范：

```text
plugin-name/
├── SKILL.md
├── agents/
└── scripts/
```

## 许可证

本项目使用 [Apache License 2.0](LICENSE) 开源协议。
