---
name: openclaw-update
description: 安全升级 OpenClaw 版本。从 S3 兼容版本清单中验证目标版本后执行升级，禁止安装未经验证的版本或 latest。触发条件：用户要求升级/更新/安装 openclaw、openclaw 版本管理、openclaw update 等。
metadata:
  {
    "openclaw": { "emoji": "🔒" }
  }
---

# OpenClaw 安全升级

仅允许升级到 S3 兼容版本清单中明确列出的 openclaw 版本。**严禁**安装 `latest` 或任何未在清单中列出的版本。

## ⚠️ 核心安全规则（不可违反）

1. **必须先获取兼容版本清单** — 升级前必须从 S3 拉取版本清单并校验。
2. **禁止安装 `latest`** — 即使用户要求，也必须拒绝，并说明原因。
3. **禁止安装未列出的版本** — 目标版本必须存在于清单的 `versions` 数组中。
4. **无法获取清单时中止** — 网络故障或清单格式异常时，禁止继续升级。

---

## 工作流程

### 步骤 1：获取兼容版本清单

脚本默认从以下 S3 地址获取：
`https://msstest.sankuai.com/taas-test/compatible-versions.json`

**清单 JSON 格式示例：**

```json
{
  "versions": ["2026.3.12", "2026.3.11", "2026.3.8"],
  "recommended": "2026.3.8",
  "minimum": "2026.3.8",
  "updated_at": "2026-03-28T10:00:00Z",
  "notes": {
    "2026.3.12": "修复模块缺失问题，推荐版本",
    "2026.3.11": "从 3.8 升级验证通过，无异常",
    "2026.3.8": "稳定基线版本"
  },
  "upgrade_paths": {}
}
```

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `versions` | `string[]` | 所有经过兼容性验证的版本列表（必需） |
| `recommended` | `string` | 推荐升级的目标版本 |
| `minimum` | `string` | 支持的最低版本 |
| `updated_at` | `string` | 清单最后更新时间 |
| `notes` | `object` | 各版本备注信息 |
| `upgrade_paths` | `object` | 升级路径，列举升级测试的结果 |

**如果脚本执行失败（非零退出码），则试图找出原因，并向用户汇报风险点。**

### 步骤 2：确认当前版本

```bash
CURRENT_VERSION=$(openclaw --version 2>/dev/null || echo "未安装")
```

将当前版本告知用户。

### 步骤 3：确定目标版本

**场景 A — 用户指定了目标版本：**

校验该版本是否在清单的 `versions` 数组中，即使用户实际想要回退版本：

```bash
echo "$VERSIONS_JSON" | python3 -c "
import json, sys
data = json.load(sys.stdin)
target = sys.argv[1]
if target == 'latest':
    print('BLOCKED_LATEST')
elif target in data.get('versions', []):
    print('ALLOWED')
else:
    print('BLOCKED_UNLISTED')
" "<目标版本>"
```

- 结果为 `BLOCKED_LATEST` → 拒绝，告知：「为保证环境稳定，禁止安装 latest 版本。请从兼容版本中选择。」
- 结果为 `BLOCKED_UNLISTED` → 拒绝，告知：「版本 X.X.X 不在兼容版本清单中，无法安装。」并展示可用版本列表。
- 结果为 `ALLOWED` → 继续下一步。

**场景 B — 用户未指定版本（如 "帮我升级 openclaw"）：**

使用清单中的 `recommended` 版本。如果无 `recommended` 字段，使用 `versions` 数组的第一项。

当 `recommended` 与当前版本相同时，需要向用户声明当前为推荐版本；如果用户指定其他可行版本，再进行升级。

**场景 C — 用户要求安装 latest：**

直接拒绝，告知安全策略禁止安装 latest，并展示可用版本列表供选择。

### 步骤 4：向用户确认升级计划

展示以下信息并等待用户确认：

```
📋 升级计划：
  当前版本: <当前版本>
  目标版本: <目标版本>
  版本备注: <notes 中对应的说明，如有>
  推荐版本: <recommended>

确认执行升级？(y/n)
```

**用户未确认前不得执行任何安装命令。**

### 步骤 5：执行升级

```bash
npm install -g openclaw@<目标版本> --force
```

### 步骤 6：重启 Gateway（重要）

升级后**必须**重启 Gateway，否则可能报模块缺失错误：

```bash
openclaw gateway restart
```

重启 Gateway 期间你将处于不可用状态，需要在运行前向用户说明。

### 步骤 7：验证升级结果

```bash
# 验证版本
openclaw --version

# 验证 Gateway 状态
openclaw gateway status
```

将验证结果告知用户。

---

## 版本查询（只读）

当用户只想查看版本信息、不升级时，可以只执行步骤 1 和步骤 2，展示：

- 当前已安装版本
- 兼容版本清单（含推荐版本和各版本备注）
- 是否有可用更新

---

## 注意事项

- 本 skill 不处理 openclaw 的首次安装，仅处理升级
- 不要进行多次升级，而是一次性升到用户所选版本
- 每次升级后必须重启 Gateway
- 版本清单由运维团队维护，遇到清单过期或缺少需要的版本时，建议用户联系运维更新清单
