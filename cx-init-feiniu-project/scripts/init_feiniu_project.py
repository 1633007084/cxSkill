#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import stat
import subprocess
import textwrap
from pathlib import Path


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    if not value:
        raise SystemExit("English project name must contain at least one ASCII letter or number.")
    return value


def title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def env_prefix(slug: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", slug.upper()).strip("_")


def db_name(slug: str) -> str:
    return slug.replace("-", "_") + ".db"


def write_file(path: Path, content: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")
    if executable:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def ensure_target(target: Path, force: bool) -> None:
    if target.exists() and any(target.iterdir()) and not force:
        raise SystemExit(f"Target directory is not empty: {target}\nUse --force only when you intentionally want to overwrite scaffold files.")
    target.mkdir(parents=True, exist_ok=True)


def render_project(target: Path, product_cn: str, slug: str, port: int, maintainer: str, distributor: str, arch: str, force: bool) -> None:
    title = title_from_slug(slug)
    env = env_prefix(slug)
    database = db_name(slug)
    desktop_key = f"{slug}.Application"

    ensure_target(target, force)

    write_file(target / ".gitignore", f"""
        # System files
        .DS_Store
        Thumbs.db

        # IDE and editor files
        .idea/
        .vscode/
        *.swp
        *.swo

        # Logs and env files
        *.log
        logs/
        .env
        .env.*
        !.env.example

        # Go build and runtime artifacts
        backend/bin/
        backend/tmp/
        backend/*.db
        backend/*.sqlite
        backend/*.sqlite3
        backend/coverage.out
        {database}*

        # Frontend dependencies and build output
        frontend/node_modules/
        frontend/dist/
        frontend/.vite/
        frontend/.cache/
        frontend/coverage/

        # Feiniu generated artifacts
        feiniu-product/app/server/server
        feiniu-product/app/www/assets/
        feiniu-product/app.pid
        feiniu-product/app.log
        feiniu-product/*.fpk
        feiniu-product/fnpack-*

        # Package manager artifacts
        npm-debug.log*
        yarn-debug.log*
        yarn-error.log*
        pnpm-debug.log*
    """)

    write_file(target / "README.md", f"""
        # {product_cn}

        `{slug}` is a Feiniu/fnOS NAS web application scaffolded with the AthTekIPMACScanner architecture.

        ## Structure

        - `backend/`: Go + Gin + SQLite API service.
        - `frontend/`: Vue 3 + Vite + TypeScript UI.
        - `feiniu-product/`: Feiniu package skeleton for `.fpk` builds.

        ## Local Development

        Backend:

        ```bash
        cd backend
        go run ./cmd/server
        ```

        Frontend:

        ```bash
        cd frontend
        npm install
        npm run dev
        ```

        Default backend port: `{port}`.
    """)

    write_file(target / "产品介绍.md", f"""
        # {product_cn}

        ## 产品定位

        {product_cn} 是一个面向飞牛 NAS 的 Web 应用，采用 Go 后端、Vue 前端和飞牛应用打包目录三段式架构。

        ## 技术架构

        - 后端：Go + Gin + SQLite
        - 前端：Vue 3 + Vite + TypeScript
        - 飞牛应用目录：`feiniu-product/`
        - 默认端口：`{port}`
        - 应用包名：`{slug}`
    """)

    write_backend(target, product_cn, slug, port, env, database)
    write_frontend(target, product_cn, slug, port)
    write_feiniu(target, product_cn, slug, port, maintainer, distributor, arch, env, desktop_key)
    format_generated_go(target)


def format_generated_go(target: Path) -> None:
    gofmt = shutil.which("gofmt")
    if not gofmt:
        return
    go_files = [str(path) for path in (target / "backend").rglob("*.go")]
    if go_files:
        subprocess.run([gofmt, "-w", *go_files], check=True)


def write_backend(target: Path, product_cn: str, slug: str, port: int, env: str, database: str) -> None:
    backend = target / "backend"

    write_file(backend / "go.mod", f"""
        module {slug}

        go 1.22

        require (
            github.com/gin-contrib/cors v1.7.2
            github.com/gin-gonic/gin v1.10.1
            modernc.org/sqlite v1.29.10
        )
    """)

    write_file(backend / "cmd/server/main.go", f"""
        package main

        import (
            "log"
            "os"
            "path/filepath"

            "{slug}/internal/api"
            "{slug}/internal/database"
        )

        func main() {{
            dataDir := os.Getenv("{env}_DATA_DIR")
            if dataDir == "" {{
                home, err := os.UserHomeDir()
                if err != nil {{
                    log.Fatal(err)
                }}
                dataDir = filepath.Join(home, ".{slug}")
            }}
            if err := os.MkdirAll(dataDir, 0o755); err != nil {{
                log.Fatal(err)
            }}

            store, err := database.Open(dataDir)
            if err != nil {{
                log.Fatal(err)
            }}
            defer store.Close()

            addr := os.Getenv("{env}_ADDR")
            if addr == "" {{
                addr = ":{port}"
            }}

            server := api.NewServer(store)
            log.Printf("{product_cn} 后端已启动: %s", addr)
            if err := server.Router().Run(addr); err != nil {{
                log.Fatal(err)
            }}
        }}
    """)

    write_file(backend / "internal/database/db.go", f"""
        package database

        import (
            "database/sql"
            "embed"
            "fmt"
            "path/filepath"

            _ "modernc.org/sqlite"
        )

        //go:embed migrations/*.sql
        var migrations embed.FS

        type Store struct {{
            DB *sql.DB
        }}

        func Open(dataDir string) (*Store, error) {{
            path := filepath.Join(dataDir, "{database}")
            db, err := sql.Open("sqlite", path+"?_pragma=busy_timeout(5000)&_pragma=foreign_keys(1)")
            if err != nil {{
                return nil, err
            }}
            if _, err := db.Exec("PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;"); err != nil {{
                return nil, err
            }}
            store := &Store{{DB: db}}
            if err := store.migrate(); err != nil {{
                _ = db.Close()
                return nil, err
            }}
            return store, nil
        }}

        func (s *Store) Close() error {{
            return s.DB.Close()
        }}

        func (s *Store) migrate() error {{
            if _, err := s.DB.Exec(`CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT NOT NULL)`); err != nil {{
                return err
            }}
            entries, err := migrations.ReadDir("migrations")
            if err != nil {{
                return err
            }}
            for _, entry := range entries {{
                version := entry.Name()
                var exists int
                if err := s.DB.QueryRow("SELECT COUNT(1) FROM schema_migrations WHERE version = ?", version).Scan(&exists); err != nil {{
                    return err
                }}
                if exists > 0 {{
                    continue
                }}
                sqlBytes, err := migrations.ReadFile("migrations/" + version)
                if err != nil {{
                    return err
                }}
                tx, err := s.DB.Begin()
                if err != nil {{
                    return err
                }}
                if _, err := tx.Exec(string(sqlBytes)); err != nil {{
                    _ = tx.Rollback()
                    return fmt.Errorf("apply migration %s: %w", version, err)
                }}
                if _, err := tx.Exec("INSERT INTO schema_migrations(version, applied_at) VALUES (?, datetime('now'))", version); err != nil {{
                    _ = tx.Rollback()
                    return err
                }}
                if err := tx.Commit(); err != nil {{
                    return err
                }}
            }}
            return nil
        }}
    """)

    write_file(backend / "internal/database/migrations/001_init.sql", """
        CREATE TABLE app_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        INSERT INTO app_state(key, value, updated_at)
        VALUES ('initialized', 'true', datetime('now'));
    """)

    write_file(backend / "internal/models/models.go", """
        package models

        type Bootstrap struct {
            ProductName string `json:"productName"`
            AppName     string `json:"appName"`
            Version     string `json:"version"`
            Ready       bool   `json:"ready"`
        }
    """)

    write_file(backend / "internal/api/server.go", f"""
        package api

        import (
            "errors"
            "net/http"
            "os"
            "path/filepath"
            "strings"

            "{slug}/internal/database"
            "{slug}/internal/models"

            "github.com/gin-contrib/cors"
            "github.com/gin-gonic/gin"
        )

        type Server struct {{
            store *database.Store
        }}

        func NewServer(store *database.Store) *Server {{
            return &Server{{store: store}}
        }}

        func (s *Server) Router() *gin.Engine {{
            router := gin.Default()
            router.Use(cors.New(cors.Config{{
                AllowOrigins: []string{{"http://localhost:5173", "http://127.0.0.1:5173"}},
                AllowMethods: []string{{"GET", "POST", "PATCH", "DELETE", "OPTIONS"}},
                AllowHeaders: []string{{"Origin", "Content-Type", "Accept"}},
            }}))
            router.GET("/health", func(c *gin.Context) {{ c.JSON(http.StatusOK, gin.H{{"ok": true}}) }})
            api := router.Group("/api")
            api.GET("/app/bootstrap", s.bootstrap)
            s.registerStaticRoutes(router)
            return router
        }}

        func (s *Server) bootstrap(c *gin.Context) {{
            c.JSON(http.StatusOK, models.Bootstrap{{
                ProductName: "{product_cn}",
                AppName: "{slug}",
                Version: "0.1.0",
                Ready: true,
            }})
        }}

        func (s *Server) registerStaticRoutes(router *gin.Engine) {{
            wwwDir := os.Getenv("{env}_WWW_DIR")
            if wwwDir == "" {{
                wwwDir = "www"
            }}
            router.NoRoute(func(c *gin.Context) {{
                if strings.HasPrefix(c.Request.URL.Path, "/api/") {{
                    c.JSON(http.StatusNotFound, gin.H{{"error": "接口不存在"}})
                    return
                }}
                requested := filepath.Clean(strings.TrimPrefix(c.Request.URL.Path, "/"))
                if requested == "." || requested == string(filepath.Separator) {{
                    requested = "index.html"
                }}
                filePath := filepath.Join(wwwDir, requested)
                if info, err := os.Stat(filePath); err == nil && !info.IsDir() {{
                    c.File(filePath)
                    return
                }}
                indexPath := filepath.Join(wwwDir, "index.html")
                if _, err := os.Stat(indexPath); err == nil {{
                    c.File(indexPath)
                    return
                }}
                c.JSON(http.StatusNotFound, gin.H{{"error": errors.New("前端页面不存在").Error()}})
            }})
        }}
    """)


def write_frontend(target: Path, product_cn: str, slug: str, port: int) -> None:
    frontend = target / "frontend"
    package_name = f"{slug}-frontend"

    write_file(frontend / "package.json", f"""
        {{
          "name": "{package_name}",
          "version": "0.1.0",
          "private": true,
          "type": "module",
          "scripts": {{
            "dev": "vite --host 0.0.0.0",
            "build": "vue-tsc && vite build",
            "preview": "vite preview --host 0.0.0.0"
          }},
          "dependencies": {{
            "@vitejs/plugin-vue": "latest",
            "typescript": "latest",
            "vite": "latest",
            "vue": "latest"
          }},
          "devDependencies": {{
            "vue-tsc": "latest"
          }}
        }}
    """)

    write_file(frontend / "index.html", f"""
        <!doctype html>
        <html lang="zh-CN">
          <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>{product_cn}</title>
          </head>
          <body>
            <div id="app"></div>
            <script type="module" src="/src/main.ts"></script>
          </body>
        </html>
    """)

    write_file(frontend / "tsconfig.json", """
        {
          "compilerOptions": {
            "target": "ES2020",
            "useDefineForClassFields": true,
            "module": "ESNext",
            "lib": ["ES2020", "DOM", "DOM.Iterable"],
            "skipLibCheck": true,
            "moduleResolution": "Bundler",
            "allowImportingTsExtensions": true,
            "resolveJsonModule": true,
            "isolatedModules": true,
            "noEmit": true,
            "strict": true,
            "jsx": "preserve"
          },
          "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
          "references": []
        }
    """)

    write_file(frontend / "vite.config.ts", f"""
        import {{ defineConfig }} from 'vite'
        import vue from '@vitejs/plugin-vue'

        export default defineConfig({{
          plugins: [vue()],
          server: {{
            proxy: {{
              '/api': 'http://127.0.0.1:{port}',
              '/health': 'http://127.0.0.1:{port}'
            }}
          }}
        }})
    """)

    write_file(frontend / "src/vite-env.d.ts", """
        /// <reference types="vite/client" />
    """)

    write_file(frontend / "src/services/api.ts", """
        export interface Bootstrap {
          productName: string
          appName: string
          version: string
          ready: boolean
        }

        async function request<T>(path: string): Promise<T> {
          const response = await fetch(path)
          if (!response.ok) {
            throw new Error(await response.text())
          }
          return response.json() as Promise<T>
        }

        export const api = {
          bootstrap: () => request<Bootstrap>('/api/app/bootstrap'),
          health: () => request<{ ok: boolean }>('/health')
        }
    """)

    write_file(frontend / "src/main.ts", """
        import { createApp } from 'vue'
        import App from './App.vue'
        import './styles.css'

        createApp(App).mount('#app')
    """)

    write_file(frontend / "src/App.vue", f"""
        <script setup lang="ts">
        import {{ onMounted, ref }} from 'vue'
        import {{ api, type Bootstrap }} from './services/api'

        const data = ref<Bootstrap | null>(null)
        const loading = ref(true)
        const error = ref('')

        onMounted(async () => {{
          try {{
            data.value = await api.bootstrap()
          }} catch (err) {{
            error.value = err instanceof Error ? err.message : String(err)
          }} finally {{
            loading.value = false
          }}
        }})
        </script>

        <template>
          <main class="page-shell">
            <section class="hero-card">
              <div class="brand-mark">{product_cn[:2]}</div>
              <p class="eyebrow">Feiniu NAS Application</p>
              <h1>{product_cn}</h1>
              <p class="lede">这是一个按 AthTekIPMACScanner 架构生成的飞牛应用项目，已包含 Go 后端、Vue 前端和 feiniu-product 打包骨架。</p>

              <div class="status-card" v-if="loading">正在连接后端...</div>
              <div class="status-card error" v-else-if="error">{{{{ error }}}}</div>
              <div class="status-card success" v-else-if="data">
                <strong>{{{{ data.productName }}}}</strong>
                <span>{{{{ data.appName }}}} · v{{{{ data.version }}}}</span>
              </div>
            </section>
          </main>
        </template>
    """)

    write_file(frontend / "src/styles.css", """
        :root {
          color: #172033;
          background: #eef3ed;
          font-family: "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei", system-ui, sans-serif;
          font-size: 15px;
        }

        * {
          box-sizing: border-box;
        }

        body {
          margin: 0;
          min-width: 360px;
          min-height: 100vh;
          background:
            radial-gradient(circle at 18% 12%, rgba(47, 111, 78, 0.22), transparent 28rem),
            radial-gradient(circle at 88% 22%, rgba(222, 151, 72, 0.20), transparent 24rem),
            linear-gradient(135deg, #f7f2e8 0%, #e7efe9 48%, #edf4f6 100%);
        }

        .page-shell {
          min-height: 100vh;
          display: grid;
          place-items: center;
          padding: 32px;
        }

        .hero-card {
          width: min(720px, 100%);
          padding: 42px;
          border: 1px solid rgba(23, 32, 51, 0.10);
          border-radius: 30px;
          background: rgba(255, 255, 255, 0.72);
          box-shadow: 0 30px 80px rgba(23, 32, 51, 0.14);
          backdrop-filter: blur(18px);
        }

        .brand-mark {
          width: 64px;
          height: 64px;
          display: grid;
          place-items: center;
          border-radius: 22px;
          color: white;
          background: #2f6f4e;
          font-weight: 800;
          letter-spacing: 0.04em;
        }

        .eyebrow {
          margin: 28px 0 10px;
          color: #8a6234;
          font-size: 12px;
          font-weight: 800;
          letter-spacing: 0.14em;
          text-transform: uppercase;
        }

        h1 {
          margin: 0;
          font-size: clamp(36px, 7vw, 72px);
          line-height: 0.95;
          letter-spacing: -0.06em;
        }

        .lede {
          max-width: 560px;
          margin: 22px 0 0;
          color: #526070;
          font-size: 17px;
          line-height: 1.8;
        }

        .status-card {
          display: grid;
          gap: 6px;
          margin-top: 30px;
          padding: 18px;
          border-radius: 18px;
          background: #f8faf8;
          color: #526070;
        }

        .status-card strong {
          color: #172033;
          font-size: 18px;
        }

        .status-card.success {
          border: 1px solid rgba(47, 111, 78, 0.18);
        }

        .status-card.error {
          border: 1px solid rgba(190, 76, 55, 0.25);
          color: #9c3f2d;
          background: #fff6f3;
        }
    """)


def write_feiniu(target: Path, product_cn: str, slug: str, port: int, maintainer: str, distributor: str, arch: str, env: str, desktop_key: str) -> None:
    feiniu = target / "feiniu-product"

    write_file(feiniu / "manifest", f"""
        appname               = {slug}
        version               = 0.1.0
        display_name          = {product_cn}
        desc                  = 面向飞牛 NAS 的 {product_cn} 应用
        arch                  = {arch}
        source                = thirdparty
        maintainer            = {maintainer}
        distributor           = {distributor}
        desktop_uidir         = ui
        desktop_applaunchname = {desktop_key}
        platform              =
    """)

    write_file(feiniu / "config/privilege", """
        {
            "defaults":
            {
                "run-as": "package"
            }
        }
    """)

    write_file(feiniu / "config/resource", f"""
        {{
            "data-share":
            {{
                "shares":
                [
                    {{
                        "name": "{slug}",
                        "permission":
                        {{
                            "rw":
                            [
                                "{slug}"
                            ]
                        }}
                    }},
                    {{
                        "name": "{slug}/data",
                        "permission":
                        {{
                            "rw":
                            [
                                "{slug}"
                            ]
                        }}
                    }}
                ]
            }}
        }}
    """)

    common_start = f"""
        #!/bin/bash

        APP_DIR="${{TRIM_APPDEST:-$(cd "$(dirname "$0")/.." && pwd)/app}}"
        EXEC="$APP_DIR/server/server"
        LOG="$APP_DIR/app.log"
        PID="$APP_DIR/app.pid"
        PORT={port}
        DATA_DIR="$APP_DIR/data"
        WWW_DIR="$APP_DIR/www"

        mkdir -p "$DATA_DIR" "$WWW_DIR"
        chmod +x "$EXEC" 2>/dev/null || true

        echo "$(date '+%F %T') starting {slug}" >> "$LOG"
        echo "app_dir=$APP_DIR exec=$EXEC port=$PORT data=$DATA_DIR www=$WWW_DIR" >> "$LOG"

        if [ -f "$PID" ]; then
            old_pid=$(cat "$PID" 2>/dev/null)
            kill "$old_pid" 2>/dev/null || true
            rm -f "$PID"
        fi

        fuser -k ${{PORT}}/tcp 2>/dev/null || true

        if [ ! -x "$EXEC" ]; then
            echo "server binary is not executable: $EXEC" >> "$LOG"
            exit 1
        fi

        cd "$APP_DIR" || exit 1
        {env}_ADDR=":$PORT" {env}_DATA_DIR="$DATA_DIR" {env}_WWW_DIR="$WWW_DIR" nohup "$EXEC" >> "$LOG" 2>&1 &
        echo $! > "$PID"
        sleep 1

        if kill -0 "$(cat "$PID")" 2>/dev/null; then
            echo "$(date '+%F %T') started pid=$(cat "$PID")" >> "$LOG"
            exit 0
        fi

        echo "$(date '+%F %T') failed to start" >> "$LOG"
        exit 1
    """
    write_file(feiniu / "cmd/main", common_start, executable=True)
    write_file(feiniu / "cmd/install_callback", common_start.replace('APP_DIR="${TRIM_APPDEST:-$(cd "$(dirname "$0")/.." && pwd)/app}"', 'APP_DIR="${TRIM_APPDEST}"'), executable=True)

    for name in ("install_init", "config_init", "config_callback", "uninstall_callback"):
        write_file(feiniu / f"cmd/{name}", """
            #!/bin/bash

            exit 0
        """, executable=True)

    stop_script = """
        #!/bin/bash

        APP_DIR="${TRIM_APPDEST}"
        PID="$APP_DIR/app.pid"

        if [ -f "$PID" ]; then
            old_pid=$(cat "$PID" 2>/dev/null)
            kill "$old_pid" 2>/dev/null || true
            rm -f "$PID"
        fi

        exit 0
    """
    write_file(feiniu / "cmd/uninstall_init", stop_script, executable=True)
    write_file(feiniu / "cmd/upgrade_init", stop_script, executable=True)
    write_file(feiniu / "cmd/upgrade_callback", """
        #!/bin/bash

        "$(dirname "$0")/install_callback"
        exit $?
    """, executable=True)

    write_file(feiniu / "app/ui/config", f"""
        {{
            ".url": {{
                "{desktop_key}": {{
                    "title": "{product_cn}",
                    "icon": "images/icon_{{0}}.png",
                    "type": "url",
                    "protocol": "",
                    "port": "{port}",
                    "url": "/",
                    "allUsers": true
                }}
            }}
        }}
    """)

    write_file(feiniu / "app/ui/index.cgi", f"""
        #!/bin/bash

        BASE_PATH="/var/apps/{desktop_key}/target/www"
        URI_NO_QUERY="${{REQUEST_URI%%\\?*}}"
        REL_PATH="/"

        case "$URI_NO_QUERY" in
            *index.cgi*)
                REL_PATH="${{URI_NO_QUERY#*index.cgi}}"
                ;;
        esac

        if [ -z "$REL_PATH" ] || [ "$REL_PATH" = "/" ]; then
            REL_PATH="/index.html"
        fi

        TARGET_FILE="${{BASE_PATH}}${{REL_PATH}}"

        if echo "$TARGET_FILE" | grep -q '\\.\\.'; then
            echo "Status: 400 Bad Request"
            echo "Content-Type: text/plain; charset=utf-8"
            echo ""
            echo "Bad Request"
            exit 0
        fi

        if [ ! -f "$TARGET_FILE" ]; then
            echo "Status: 404 Not Found"
            echo "Content-Type: text/plain; charset=utf-8"
            echo ""
            echo "404 Not Found: ${{REL_PATH}}"
            exit 0
        fi

        ext="${{TARGET_FILE##*.}}"
        case "$ext" in
            html|htm) mime="text/html; charset=utf-8" ;;
            css) mime="text/css; charset=utf-8" ;;
            js) mime="application/javascript; charset=utf-8" ;;
            png) mime="image/png" ;;
            jpg|jpeg) mime="image/jpeg" ;;
            svg) mime="image/svg+xml" ;;
            json) mime="application/json; charset=utf-8" ;;
            *) mime="application/octet-stream" ;;
        esac

        echo "Content-Type: $mime"
        echo ""
        cat "$TARGET_FILE"
    """, executable=True)

    write_file(feiniu / "app/www/index.html", f"""
        <!doctype html>
        <html lang="zh-CN">
          <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>{product_cn}</title>
          </head>
          <body>
            <main style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 32px;">
              <h1>{product_cn}</h1>
              <p>请先构建前端并同步 dist 到 feiniu-product/app/www。</p>
            </main>
          </body>
        </html>
    """)

    write_file(feiniu / "app/server/.gitkeep", "")
    write_file(feiniu / "app/ui/images/.gitkeep", "")

    write_file(feiniu / "飞牛产品说明.md", f"""
        # {product_cn}飞牛 NAS 应用说明

        本目录是 `{product_cn}` 的飞牛 NAS 应用包骨架。

        ## 应用信息

        - 应用名称：{product_cn}
        - 包名：`{slug}`
        - 桌面应用名：`{desktop_key}`
        - 默认端口：`{port}`
        - 应用类型：iframe Web 应用
        - 后端：Go + Gin
        - 前端：Vue 3 + Vite 构建后的静态文件
        - 本地数据：SQLite，建议存放在飞牛应用目标目录的 `data/` 下

        ## 同步关系

        - `backend/` 构建出的服务二进制复制到 `feiniu-product/app/server/server`。
        - `frontend/` 构建后的 `dist/` 内容复制到 `feiniu-product/app/www/`。
        - 飞牛应用端口、前端代理和产品说明默认使用 `{port}`。
    """)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a Feiniu app project with Go backend, Vue frontend, and feiniu-product skeleton.")
    parser.add_argument("--target", required=True, help="Target project directory.")
    parser.add_argument("--product-cn", required=True, help="Chinese product display name.")
    parser.add_argument("--project-en", required=True, help="English project name. It will be normalized to kebab-case.")
    parser.add_argument("--port", type=int, default=9381, help="Default backend and Feiniu app port.")
    parser.add_argument("--maintainer", default="星启创科", help="Feiniu manifest maintainer.")
    parser.add_argument("--distributor", default="athtek", help="Feiniu manifest distributor.")
    parser.add_argument("--arch", default="x86_64", choices=["x86_64", "amd64", "arm64", "aarch64"], help="Feiniu manifest architecture.")
    parser.add_argument("--force", action="store_true", help="Allow writing into a non-empty target directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target = Path(args.target).expanduser().resolve()
    slug = slugify(args.project_en)
    arch = "x86_64" if args.arch == "amd64" else "arm64" if args.arch == "aarch64" else args.arch
    render_project(
        target=target,
        product_cn=args.product_cn.strip(),
        slug=slug,
        port=args.port,
        maintainer=args.maintainer,
        distributor=args.distributor,
        arch=arch,
        force=args.force,
    )
    print(f"Created Feiniu project: {target}")
    print(f"Product CN: {args.product_cn.strip()}")
    print(f"Project slug: {slug}")
    print(f"Default port: {args.port}")
    print("Next: run npm install in frontend/ and go mod tidy in backend/ when ready.")


if __name__ == "__main__":
    main()
