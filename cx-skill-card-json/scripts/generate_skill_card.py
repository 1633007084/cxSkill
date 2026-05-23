#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


CARDS = {
    "frontend-design": {
        "name": "前端设计技能",
        "description": "用于设计和优化现代 Web 页面、落地页、后台界面和组件视觉，提升排版、配色、层级、响应式和整体产品感。",
        "usage": "用前端设计技能重新设计这个页面",
        "tags": ["前端设计", "UI", "视觉优化"],
    },
    "figma-implement-design": {
        "name": "Figma 设计实现技能",
        "description": "根据 Figma 链接或选中节点实现高还原度前端代码，将设计稿转成可运行的页面或组件。",
        "usage": "用 figma-implement-design 根据这个 Figma 链接实现页面",
        "tags": ["Figma", "设计还原", "前端实现"],
    },
    "web-design-guidelines": {
        "name": "网页设计规范技能",
        "description": "用于检查和优化网站的视觉规范、信息层级、响应式布局、可读性、转化路径和整体高级感。",
        "usage": "用网页设计规范技能检查这个官网",
        "tags": ["网页设计", "设计规范", "官网优化"],
    },
    "react-best-practices": {
        "name": "React 最佳实践技能",
        "description": "用于编写、重构和评审 React / Next.js 代码，关注组件边界、Hooks、状态管理、性能和可访问性。",
        "usage": "用 React 最佳实践技能重构这个组件",
        "tags": ["React", "Next.js", "最佳实践"],
    },
    "playwright": {
        "name": "Playwright 浏览器验证技能",
        "description": "通过真实浏览器执行页面打开、点击、输入、截图、快照和交互验证，用于本地页面调试与 UI 回归检查。",
        "usage": "用 Playwright 技能打开本地页面并截图检查",
        "tags": ["Playwright", "浏览器验证", "自动化测试"],
    },
    "kane-cli": {
        "name": "Kane CLI 测试技能",
        "description": "用于通过 Kane CLI / KaneAI 创建和运行自然语言浏览器测试，覆盖登录、下单、搜索等关键用户流程。",
        "usage": "用 Kane CLI 技能给这个流程生成测试",
        "tags": ["Kane CLI", "AI 测试", "浏览器测试"],
    },
    "gh-fix-ci": {
        "name": "GitHub CI 修复技能",
        "description": "用于检查 GitHub Actions 失败原因，读取 PR 检查日志，定位 CI 错误并协助制定修复方案。",
        "usage": "用 gh-fix-ci 修复这个 PR 的 CI 失败",
        "tags": ["GitHub Actions", "CI", "PR 修复"],
    },
    "gh-address-comments": {
        "name": "GitHub 评论处理技能",
        "description": "用于读取并处理当前 PR 的 review comments 或 issue comments，汇总评论、定位代码并协助逐条修复。",
        "usage": "用 gh-address-comments 处理当前 PR 的 review comments",
        "tags": ["GitHub", "Code Review", "PR 评论"],
    },
    "figma-generate-design": {
        "name": "Figma 页面生成技能",
        "description": "用于根据代码、页面描述或已有 Web 页面在 Figma 中生成完整页面、视图或多区块布局。",
        "usage": "用 figma-generate-design 把这个页面生成到 Figma",
        "tags": ["Figma", "页面生成", "设计稿"],
    },
    "figma-generate-library": {
        "name": "Figma 设计系统生成技能",
        "description": "用于基于代码库创建或更新 Figma 设计系统，包括颜色变量、排版、组件库、主题和设计规范。",
        "usage": "用 figma-generate-library 基于代码生成 Figma 设计系统",
        "tags": ["Figma", "设计系统", "组件库"],
    },
}


def read_skill_id(value: str) -> str:
    path = Path(value).expanduser()
    skill_md = path / "SKILL.md" if path.is_dir() else path
    if skill_md.exists() and skill_md.name == "SKILL.md":
        text = skill_md.read_text(encoding="utf-8")
        match = re.search(r"^name:\s*[\"']?([^\"'\n]+)[\"']?\s*$", text, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return skill_md.parent.name
    return value.strip()


def display_from_id(skill_id: str) -> str:
    words = [part for part in re.split(r"[-_\s]+", skill_id) if part]
    if not words:
        return "未命名技能"
    display = " ".join(word.upper() if word.lower() in {"ai", "api", "cli", "ui", "ci", "pr"} else word.capitalize() for word in words)
    return f"{display} 技能"


def infer_tags(skill_id: str) -> list[str]:
    lowered = skill_id.lower()
    tags: list[str] = []
    if "figma" in lowered:
        tags += ["Figma", "设计"]
    if "react" in lowered:
        tags += ["React", "前端"]
    if "frontend" in lowered or "web" in lowered:
        tags += ["前端", "Web"]
    if "playwright" in lowered:
        tags += ["Playwright", "浏览器验证"]
    if "gh" in lowered or "github" in lowered:
        tags += ["GitHub", "自动化"]
    if "kane" in lowered:
        tags += ["Kane CLI", "AI 测试"]
    if not tags:
        tags = ["技能", "自动化", "效率工具"]
    return list(dict.fromkeys(tags))[:4]


def card_for(value: str) -> dict[str, object]:
    skill_id = read_skill_id(value)
    known = CARDS.get(skill_id)
    if known:
        name = known["name"]
        description = known["description"]
        usage = known["usage"]
        tags = known["tags"]
    else:
        name = display_from_id(skill_id)
        description = f"用于辅助完成与 {skill_id} 相关的专业工作流，提升任务执行的一致性和效率。"
        usage = f"用 {skill_id} 技能处理这个任务"
        tags = infer_tags(skill_id)

    return {
        "name": name,
        "description": description,
        "installMethod": f"对 AI 说：“安装 {skill_id} 技能。”安装后可说“{usage}”。",
        "badge": "三方精选",
        "tags": tags,
    }


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: generate_skill_card.py <skill-id-or-skill-path> [...]", file=sys.stderr)
        return 2
    cards = [card_for(arg) for arg in argv]
    payload: object = cards[0] if len(cards) == 1 else cards
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
