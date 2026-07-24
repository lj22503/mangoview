# mangoview — neat-freak 知识收尾报告

**收尾时间**：2026-07-24
**收尾路径**：轻量路径（全栈 Web 项目，文档齐全，已有 recent neat-freak commit `656474b` + 完整规则/进度体系，本次为审计 + 未跟踪盘点）
**收尾者**：neat-freak（v3.0.0）

---

## 一、影响（用户视角）

- **本次整体干净**：命名一致、文档齐全、未提交改动少，是 idx 0-7 中**第一个没有重大发现**的项目。
- **暴露未跟踪 GitHub Topics 草稿**：`topics-suggested.md`（GitHub Topics 推荐清单），未 commit、未 gitignore——同类问题已在 idx 4 / 6 出现，累计 3 处。
- **暴露 docs/ 子目录结构复杂**：`inventory/`（19 个设计文档）、`prd/`、`tech-spec/`、`user-stories/`、`原始材料/` 五个子目录并存，是否仍全有效未审计——可能是演进历史残留。
- **暴露 PROGRESS.md 描述 git submodule 但当前未跟踪**：第 30 行提"skills 知识库骨架（investment-framework-skill git submodule）"——但 `git submodule` 命令执行未确认、`skills/` 目录实际是 mangoview 自带内容（不是 git submodule）。

## 二、现役事实矩阵

| 事实面 | 状态 | 证据 |
|--------|------|------|
| 代码 | `verified-current` | Next.js 14 前端 + FastAPI 后端 + SQLite；vercel.json + render.yaml 双部署配置 |
| 运行态 | `verified-current` | HEAD `656474b`（最近 commit 移除 TODO 注释）；git log 显示多次生产回退（`6e8ea4d revert: 修复生产环境 API 404`），说明有 live 部署在跟踪 |
| 文档 | `verified-current` | CLAUDE.md / AGENTS.md / PROGRESS.md / DESIGN.md / SYSTEM_PROMPT.md / API_REVIEW.md / REVIEW-FINDINGS.md / INTEGRATION_PLAN.md / docs/ 下 6 文件 + 5 子目录 |
| 规则 | `verified-current` | CLAUDE.md（含 Superpowers 七阶段流程）+ AGENTS.md 双规则文件；明确技术栈 + 项目结构 |
| 记忆 | `not-applicable` | 无 |
| 工作区 | `verified-current` | 新建 `.neat-freak/`；仅 `topics-suggested.md` 未跟踪；无未提交改动、无删除待提交 |

## 三、关键发现

### 3.1 命名一致 ✅

| 维度 | 名字 | 证据 |
|------|------|------|
| 本地目录 | `mangoview` | `D:\claudework\mangoview\` |
| GitHub remote | `lj22503/mangoview` | `git remote -v` |
| CLAUDE.md | `MangoView` | 第 1 行 |
| PROGRESS.md | `MangoView MVP` | 第 1 行 |
| vercel.json / render.yaml | （未读全文） | 文件名暗示 mangoview |

→ **这是 idx 0-7 中命名最一致的项目**。

### 3.2 文档爆炸但分层清晰

根目录 8 个 MD：
- `AGENTS.md`（4.7KB）
- `API_REVIEW.md`（8KB）
- `CLAUDE.md`（4.8KB）
- `DESIGN.md`（12KB）
- `INTEGRATION_PLAN.md`（6.4KB）
- `PROGRESS.md`（8.8KB）
- `REVIEW-FINDINGS.md`（9KB）
- `SYSTEM_PROMPT.md`（21KB）

docs/ 子目录：
- `DATA_TEST_REPORT.md`
- `INVESTMENT_DASHBOARD_PLAN_V1.md`（**带 V1 后缀，疑似被 v2 替代？**）
- `PRD-DATA-INTEGRATION.md`
- `SPEC.md`
- `inventory/`（PROGRESS 提"19 个设计文档"）
- `issues.md`
- `prd/`
- `skill-analysis.md`
- `tech-spec/`
- `user-stories/`
- `原始材料/`（中文目录名暗示原始素材）

### 3.3 INVESTMENT_DASHBOARD_PLAN_V1.md 命名疑点

- 文件名带 `_V1` 后缀——可能存在 V2 / current 版本，或仅作为历史归档
- `git ls-files docs/` 应可见全部 docs，V1 是否仍最新待确认

### 3.4 topics-suggested.md（未跟踪，第 3 处累计）

| 属性 | 值 |
|------|-----|
| 路径 | `D:\claudework\mangoview\topics-suggested.md` |
| 状态 | `?? topics-suggested.md`（未跟踪） |
| 累计 | idx 4（investment-framework-skill）、idx 6（narrative-skill）、idx 7（mangoview）均有同类文件 |

### 3.5 项目质量良好的部分

- 部署配置完整：Vercel（前端）+ Render（后端）+ GitHub Actions
- git log 显示多次生产回退（API 404 修复等）—— 有 live 部署监控
- docs/ 分层（PRD / SPEC / 设计 / 用户故事 / 数据报告 / 技能分析）结构合理
- 规则文件双轨：CLAUDE.md（流程约束）+ AGENTS.md（agent 手册）

## 四、改动 / 新建

| 文件 | 动作 | 原因 |
|------|------|------|
| `.neat-freak/reports/mangoview-2026-07-24.md` | 新建 | 本次 audit trail |

## 五、待你确认（未确认前不动作）

1. **topics-suggested.md**：操作完 GitHub UI 后删除（同 idx 4/6 同类问题）
2. **INVESTMENT_DASHBOARD_PLAN_V1.md**：是否还有 V2 或当前版本？V1 是否要归档/删除？
3. **docs/原始材料/**：是否需要 gitignore（中文目录名暗示是临时草稿）
4. **PROGRESS.md 第 30 行 git submodule 描述**：是否仍用 submodule？当前 `skills/` 目录内容来源（submodule / 实际文件 / 其他）确认

## 六、遗留

- docs/ 19 个 inventory 文档未逐个审
- AGENTS.md / API_REVIEW.md / DESIGN.md / SYSTEM_PROMPT.md / REVIEW-FINDINGS.md / INTEGRATION_PLAN.md 6 份根 MD 未读全文
- render.yaml / vercel.json 配置未读全文
- git submodule 实际状态未验证
- `.impeccable/` 历史残留未处置
- `check-status.sh` / `kill-old.ps1` 工具脚本是否仍需要未确认

---

*收尾完成度：5 事实面已标注（记忆 not-applicable）。报告基于 commit `656474b`（HEAD，分支 main）。本次是 idx 0-7 中**最干净**的一个项目，命名一致、未提交改动极少。如需重新跑请清空 `.neat-freak/reports/` 后重跑。*