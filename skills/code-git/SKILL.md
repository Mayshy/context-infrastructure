---
name: code-git
description: Git 与 SSH 配置指南。当用户需要进行 git 相关操作（clone、push、pull、commit、分支管理等）、配置 SSH 密钥、新增 SSH 账户、或排查 SSH 连接问题时，必须调用此 skill。
---

# Code Git

帮助用户配置 SSH 密钥与连接。

## 持久化目录

`~/.openclaw/` 是本环境唯一的持久化目录，所有需要跨会话保留的数据都必须存放在此目录下。

### 默认 Git Clone 目录

所有 `git clone` 操作默认将仓库克隆到 `~/.openclaw/` 目录下，除非用户显式指定了其他路径，并已经向用户阐述过风险。

```bash
# 默认 clone 到 ~/.openclaw/ 下
git clone <repo-url> ~/.openclaw/<repo-name>
```

如果 `~/.openclaw/` 目录不存在，先创建：

```bash
mkdir -p ~/.openclaw
```

## 背景知识

### 美团 Code 平台

美团内部代码仓库平台（类似 GitLab）。

**网页地址与 Git 地址的对应关系：**

网页仓库地址和 Git SSH 地址的域名不同，需要注意区分：

- 网页仓库地址：`https://dev.sankuai.com/code/repo-detail/<group>/<repo>/file/list`
- Git SSH 地址（SCP 风格）：`git@git.sankuai.com:<group>/<repo>.git`
- Git SSH 地址（URL 风格）：`ssh://git@git.sankuai.com/<group>/<repo>.git`

示例：

| 类型 | 地址 |
|------|------|
| 网页仓库 | `https://dev.sankuai.com/code/repo-detail/user-name/gundam-d2c-mcp/file/list` |
| Git SSH | `ssh://git@git.sankuai.com/user-name/resp-name.git` |

**转换规则：**
- 网页 → Git：从网页 URL 中提取 `<group>/<repo>`（即 `/code/repo-detail/` 之后、`/file/list` 之前的部分），拼接为 `git@git.sankuai.com:<group>/<repo>.git`
- Git → 网页：从 Git 地址中提取 `<group>/<repo>`，拼接为 `https://dev.sankuai.com/code/repo-detail/<group>/<repo>/file/list`

## SSH 配置工作流

当用户需要配置 SSH（如新增一个 GitHub 账号、美团 Code 账号或其他远程服务器的 SSH 连接）时，按以下步骤操作：

### 0. 检查现有配置（配置前必做）

在进行任何 SSH 配置修改之前，**必须先检查**是否已有配置或备份：

```bash
# 检查持久化备份目录中是否已有 SSH 配置
ls -la ~/.openclaw/.ssh/ 2>/dev/null

# 检查当前 ~/.ssh/ 目录状态
ls -la ~/.ssh/ 2>/dev/null

# 检查现有 ssh config
cat ~/.ssh/config 2>/dev/null
```

如果 `~/.openclaw/.ssh/` 中已有备份，你需要先告诉用户相关信息（如用户、邮箱、公钥等），若无其他指示，则**优先从备份恢复**而非重新生成。

恢复后验证连通性，如果连通则无需重新配置。

### 1. 生成 SSH 密钥对

为新账户生成独立的密钥对，使用有辨识度的文件名：

```bash
ssh-keygen -t ed25519 -C "<email>" -f ~/.ssh/id_ed25519_<名称>
```

- 用户如不指定密码，加 `-N ""`

### 2. 配置 `~/.ssh/config`

默认只为美团 Code 平台添加配置，除非显性指定添加其他平台。

在 `~/.ssh/config` 末尾追加新配置：

```
Host <域名或别名>
    HostName <实际域名>
    User git
    IdentityFile ~/.ssh/id_ed25519_<名称>
    IdentitiesOnly yes
    HostkeyAlgorithms +ssh-ed25519
    PubkeyAcceptedKeyTypes +ssh-ed25519
```

示例 — 为美团 Code 配置：

```
Host git.sankuai.com
    HostName git.sankuai.com
    User git
    IdentityFile ~/.ssh/id_ed25519_meituan
    IdentitiesOnly yes
    HostkeyAlgorithms +ssh-ed25519
    PubkeyAcceptedKeyTypes +ssh-ed25519
```

**规则：**
- 操作 `~/.ssh/config` 时**不要覆盖整个文件**，只追加或修改指定的 Host 块
- 如果目标 Host 已存在，先确认用户是否要修改，再进行操作

### 3. 将公钥添加到远程平台

读取公钥内容并展示给用户，指引其添加到对应平台：

```bash
cat ~/.ssh/id_ed25519_<名称>.pub
```

- **GitHub**：Settings → SSH and GPG keys → New SSH key
- **美团 Code**：`https://dev.sankuai.com/code/home` → 页面右上角 → SSH Key

### 4. 验证连通性

```bash
ssh -T git@<域名或别名>
```

如：

```bash
ssh -T git@git.sankuai.com
```

### 5. 备份 SSH 配置到持久化目录（配置后必做）

每次对 `~/.ssh/` 进行任何修改（生成密钥、修改 config 等）后，**必须**将整个 `.ssh` 目录备份到持久化目录：

```bash
# 创建持久化备份目录
mkdir -p ~/.openclaw/.ssh

# 完整备份 ~/.ssh/ 到 ~/.openclaw/.ssh/
cp -a ~/.ssh/* ~/.openclaw/.ssh/

# 确认备份成功
ls -la ~/.openclaw/.ssh/
```

**备份规则：**
- 每次 SSH 配置变更后都必须执行备份
- 使用 `cp -a` 保留文件权限
- 备份包括：私钥、公钥、config 文件、known_hosts 等所有文件
- 如果备份内容有冲突，则向用户询问方案

## 注意事项

- 永远不要主动读取或展示私钥内容
- 永远不要删除已有的 SSH 密钥文件
- 操作 `~/.ssh/config` 时不要覆盖整个文件
- 如遇到权限问题，提示用户检查密钥文件权限（`chmod 600`）
- 首次 SSH 连接新服务器时会出现 host key 确认提示，输入 `yes` 即可
- `git clone` 默认目标目录为 `~/.openclaw/`，这是唯一的持久化目录
- 任何 SSH 配置变更后必须备份到 `~/.openclaw/.ssh/`
- 新会话开始时应优先检查 `~/.openclaw/.ssh/` 中是否有可恢复的备份
