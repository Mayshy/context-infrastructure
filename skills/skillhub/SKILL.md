---
name: skillhub
description: SkillHub（Friday 技能广场 / skill 广场）Skill 全功能管理工具，支持搜索/发现/安装/更新/卸载 Skill，以及发布/推送新版本到广场。当用户提到找 skill、搜索 skill、安装 skill、查看 skill、skill 市场、回滚、拉取更新，或需要发布/上架/推送 skill 到广场，或发送了 SkillHub / Friday / skills.sankuai.com 详情页 URL 时使用。
---

# SkillHub — Skill 全功能管理工具

底层统一使用 `mtskills`（`@mtfe/mtskills`）完成所有平台交互。

**前置依赖**：`npm install -g @mtfe/mtskills --registry=http://r.npm.sankuai.com`（最低版本 7.7.9）

> ⚠️ 使用前运行 `mtskills --version` 确认版本 ≥ 7.7.9，否则先升级再继续。

---

## 意图路由

| 用户意图 | 操作 | 参考文档 |
|---|---|---|
| 搜索 / 发现 Skill | `mtskills search <关键词>` 或 `--tag <标签>` 或 `--verified` | `references/search-and-discover.md` |
| 交互式浏览市场 | `mtskills i mt [--keyword <词>] [--tag <标签>] [--verified]` | `references/search-and-discover.md` |
| 查看 Skill 详情 | `mtskills read <skill名称>` | `references/search-and-discover.md` |
| 通过 URL 链接安装 | 解析 URL 中的 skill id → `mtskills i mt --id <id> -g` | 见下方「URL 安装」 |
| 安装 Skill | `mtskills i <skill名称>[@<版本>] -g`（项目安装省略 `-g`） | `references/install-and-manage.md` |
| 批量安装 | `mtskills i skill-a,skill-b,skill-c -g` | `references/install-and-manage.md` |
| 列出已安装 | `mtskills list` | `references/install-and-manage.md` |
| 卸载 Skill | `mtskills remove <skill名称>` | `references/install-and-manage.md` |
| 同步到 AGENTS.md | `mtskills sync [-y] [-o <输出文件>]` | `references/install-and-manage.md` |
| 拉取更新（单个） | `mtskills pull <skill名称>` | `references/install-and-manage.md` |
| 拉取更新（全部） | `mtskills pull --all` | `references/install-and-manage.md` |
| 配置定时自动更新 | macOS/Linux: `crontab -e`，Windows: `schtasks` | `references/install-and-manage.md` |
| 安装前安全评估 | 读取并按 `references/pre-install-vetting.md` 规则审查 Skill 目录 | `references/pre-install-vetting.md` |
| 首次发布新 Skill | ⚠️ **执行前须向用户确认**，确认后执行 `mtskills publish`（默认 private；需公开显式指定 `--visibility public`） | `references/publish-workflow.md` |
| 推送新版本 | ⚠️ **执行前须向用户确认**，确认后执行 `mtskills push --intro auto` | `references/publish-workflow.md` |
| 发布前安全扫描（可选） | `python scripts/security-scan.py [<skill目录>]` | `references/security-scan-rules.md` |
| 美团内部专项检查（可选） | `python scripts/security-check.py <skill目录>` | `references/security-scan-rules.md` |

---

## URL 安装说明

| URL 格式 | skill id 提取规则 |
|---|---|
| `https://friday.sankuai.com/skills/skill-detail?...&id=<id>` | 取 query 参数 `id` 的值 |
| `https://skills.sankuai.com/skill-detail?...&id=<id>` | 取 query 参数 `id` 的值 |
| `https://skillhub.sankuai.com/skills/<id>` | 取路径最后一段 |

解析到 id 后执行：`mtskills i mt --id <id> -g`

---

## 认证

详见各 references 文件。核心原则：**发布时用用户身份**（不带 `--app-auth`），否则 `isManager=false`，无法后续编辑自己的 Skill。无头环境（CatPaw/CatClaw）加 `--ciba <your-mis>`。

### CIBA 认证说明

CIBA 认证需要用户在美团内部的身份 ID（**mis Id**，即美团员工工号/登录名，如 `zhangsan`）。

⚠️ **重要规则**：
- 当需要使用 CIBA 认证但**不知道用户的 mis Id** 时，必须**主动询问**用户，**严禁猜测或伪造**。
- 用户提供 mis Id 后，在本次会话中**记住并复用**，不要反复询问。
- 询问示例：「请问您的美团 mis Id 是什么？（例如：`zhangsan`）」
