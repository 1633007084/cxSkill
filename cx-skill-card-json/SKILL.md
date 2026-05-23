---
name: cx-skill-card-json
description: Generate marketplace-style JSON metadata for a Codex/Claude Code skill from a skill name, Chinese display name, or SKILL.md folder. Use when the user asks to return skill card data with fields like name, description, installMethod, badge, and tags.
---

# Skill Card JSON

## Overview

Use this skill to produce one JSON object, or an array of JSON objects, describing skills in this format:

```json
{
  "name": "Figma 设计系统生成技能",
  "description": "用于基于代码库创建或更新 Figma 设计系统，包括颜色变量、排版、组件库、主题和设计规范。",
  "installMethod": "对 AI 说：“安装 figma-generate-library 技能。”安装后可说“用 figma-generate-library 基于代码生成 Figma 设计系统”。",
  "badge": "三方精选",
  "tags": ["Figma", "设计系统", "组件库"]
}
```

## 使用方法

中文叫法：`技能卡片数据生成技能`。

可以这样叫：

- `用技能卡片数据生成技能，给 figma-generate-library 生成一条 JSON。`
- `给技能名称 frontend-design，返回技能卡片数据。`
- `根据 skills/figma-implement-design/SKILL.md 生成 marketplace JSON。`
- `Use $cx-skill-card-json to generate JSON cards for these skill names: frontend-design, playwright.`

## Rules

- Return valid JSON only when the user asks for data to copy.
- Use `badge: "三方精选"` by default, unless the user specifies another badge.
- Use Chinese display names ending in `技能`.
- Keep `description` concise and user-facing, not implementation-heavy.
- `installMethod` must be conversational, not a terminal command:
  - `对 AI 说：“安装 <skill-id> 技能。”安装后可说“用 <usage phrase>”。`
- Prefer the actual skill id from YAML frontmatter `name`.
- If a `SKILL.md` path or skill directory is available, read it and derive the description/tags from the real contents.
- If only a skill id is given, infer a reasonable Chinese display name, description, install prompt, and 2-4 tags.

## Output Shape

For one skill, return one object:

```json
{
  "name": "...",
  "description": "...",
  "installMethod": "...",
  "badge": "三方精选",
  "tags": ["...", "...", "..."]
}
```

For multiple skills, return an array of those objects.

## Helper Script

Use `scripts/generate_skill_card.py` for deterministic cards from known skill ids or local `SKILL.md` paths:

```bash
scripts/generate_skill_card.py figma-generate-library
scripts/generate_skill_card.py skills/figma-generate-library
scripts/generate_skill_card.py frontend-design playwright gh-fix-ci
```

The script contains curated mappings for common skills and falls back to simple inference when a name is unknown.
