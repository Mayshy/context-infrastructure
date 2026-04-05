# macOS Terminal 视觉配置与生产力工具调研
# 面向 AI 开发者 | 2026-04-05

## 核心结论（先读这里）

5 个并行 agent 交叉验证后的共识：

| 工具 | ROI 等级 | 理由 |
|------|---------|------|
| uv | ⭐⭐⭐⭐⭐ | 替代 pyenv+pip+venv，快 10-100x |
| Starship | ⭐⭐⭐⭐⭐ | 跨 shell，零配置即好用 |
| fzf | ⭐⭐⭐⭐⭐ | 装了立刻改变工作方式 |
| bat+eza+rg+fd | ⭐⭐⭐⭐⭐ | 一组命令，全面升级 |
| Ghostty | ⭐⭐⭐⭐ | 2025 最佳终端，替代 iTerm2 |
| delta | ⭐⭐⭐⭐ | git diff 体验质变 |
| lazygit | ⭐⭐⭐⭐ | TUI git，减少 80% 命令记忆 |
| tmux | ⭐⭐⭐⭐ | session 持久化，AI 开发必备 |
| Catppuccin | ⭐⭐⭐ | 2025 最热主题，全生态覆盖 |
| zinit | ⭐⭐⭐ | zsh 启动从 1.4s 降到 53ms |

---

## 一键安装（先跑这个）

brew install starship fzf bat eza fd ripgrep delta lazygit gh htop btop dust jq direnv zoxide
brew install --cask ghostty font-jetbrains-mono-nerd-font
curl -LsSf https://astral.sh/uv/install.sh | sh

---

## 1. Prompt 配置：Starship vs Powerlevel10k

### 结论：AI 开发者选 Starship

**Starship 优势：**
- 跨 shell（bash/zsh/fish 一套配置）
- Rust 编写，极快
- TOML 配置，直观
- 2025 年社区活跃度远超 p10k

**Powerlevel10k 优势：**
- Instant Prompt（zsh 专属，启动速度极快）
- 更丰富的 zsh 专属功能

**2025 年社区声音：**
- HN「Starship: Dead End?」(2025-06-01) https://news.ycombinator.com/item?id=44154007
- Reddit「Upgraded my macOS terminal setup with Ghostty and Starship」(2026-02-08) https://www.reddit.com/r/zsh/comments/1qzhvh5/

### Starship 安装

brew install starship
echo '''eval ""''' >> ~/.zshrc

### AI 开发者专用 starship.toml

cat > ~/.config/starship.toml << '''EOF'''
"" = '''https://starship.rs/config-schema.json'''

add_newline = false
format = " 127 "

[git_branch]
symbol = " "
format = "[]() "
style = "bold green"

[git_status]
format = "([\[\]]() )"

[cmd_duration]
min_time = 2_000
format = "[took ]() "
style = "yellow"

[status]
disabled = false
symbol = "✗"
format = "[ 127]() "

[python]
format = "[()(\(\))]() "
symbol = " "

[nodejs]
format = "[()]() "
symbol = " "

[aws]
format = "[()(\(\))]() "
symbol = "☁️  "

[time]
disabled = false
format = "[]() "
time_format = "%H:%M"
EOF

### Powerlevel10k（如果坚持用 zsh）

brew install romkatv/powerlevel10k/powerlevel10k
echo '''source /opt/homebrew/share/powerlevel10k/powerlevel10k.zsh-theme''' >> ~/.zshrc
# 首次运行自动配置向导
p10k configure

---

## 2. 终端字体：Nerd Fonts

### 为什么需要

Nerd Fonts 把 Font Awesome、Material Design Icons 等 3600+ 图标打包进字体。
Starship/p10k 的 git 图标、语言图标都依赖它。

### 推荐字体（2025）

| 字体 | 特点 | 安装命令 |
|------|------|---------|
| JetBrains Mono NF | 专为代码设计，ligature | brew install --cask font-jetbrains-mono-nerd-font |
| Fira Code NF | 经典 ligature | brew install --cask font-fira-code-nerd-font |
| Hack NF | 简洁清晰 | brew install --cask font-hack-nerd-font |
| Cascadia Code NF | 微软出品，现代感 | brew install --cask font-cascadia-code-nerd-font |

### iTerm2 设置字体

iTerm2 → Settings → Profiles → Text → Font → 选择 JetBrains Mono Nerd Font

### 一键安装所有 Nerd Fonts（可选）

brew tap homebrew/cask-fonts
brew search '/font-.*-nerd-font/' | awk '{ print  }' | xargs -I{} brew install --cask {} || true

来源：https://github.com/ryanoasis/nerd-fonts
Gist：https://gist.github.com/davidteren/898f2dcccd42d9f8680ec69a3a5d350e

---

## 3. 颜色主题

### 2025 年排行

1. **Catppuccin** - 最热，pastel 调色，四种 flavor（Latte/Frappé/Macchiato/Mocha）
2. **Nord** - 冷色系，眼睛友好，长期工作首选
3. **Dracula** - 经典暗色，生态最广
4. **Tokyo Night** - 现代感，VS Code 生态好
5. **Gruvbox** - 复古暖色，护眼

### iTerm2 安装 Catppuccin（官方步骤）

git clone https://github.com/catppuccin/iterm.git
# 然后在 iTerm2：Profiles → Colors → Color Preset → Import
# 选择 iterm/colors/macchiato.itermcolors
# 再从 Color Presets 选择导入的主题

官方 URL：https://github.com/catppuccin/iterm
Catppuccin 官网：https://catppuccin.com

### 其他主题安装

# Nord
# 下载：https://github.com/nordtheme/iterm2/releases/latest
# 导入 Nord.itermcolors 同上

# Dracula
# https://draculatheme.com/iterm

# 450+ 主题集合
# https://iterm2colorschemes.com/
# https://github.com/mbadolato/iTerm2-Color-Schemes

### iTerm2 高价值配置（装了立刻有用）

1. **Hotkey Window**（全局快捷键调出终端）
   Settings → Keys → Create a Dedicated Hotkey Window
   文档：https://iterm2.com/documentation-hotkey.html

2. **Shell Integration**（命令标记、历史跳转）
   curl -L https://iterm2.com/shell_integration/install_shell_integration.sh | bash
   文档：https://iterm2.com/documentation-shell-integration.html

3. **Natural Text Editing**（Option+←/→ 按词移动）
   Preferences → Profiles → Keys → Key Mappings → Presets → Natural Text Editing

4. **Status Bar**（CPU/内存/网络）
   Settings → Profiles → Session → Status bar enabled → Configure Status Bar
   文档：https://iterm2.com/documentation-status-bar.html

---

## 4. fzf 深度使用

### 安装与基础绑定

brew install fzf
# 安装 shell 集成（Ctrl-T / Ctrl-R / Alt-C）
/opt/homebrew/opt/fzf/install

# 或在 zsh 中
source <(fzf --zsh)

### 三个核心绑定

| 绑定 | 功能 |
|------|------|
| Ctrl-R | 历史命令搜索 |
| Ctrl-T | 文件/目录搜索，粘贴到命令行 |
| Alt-C | 跳转到选中目录 |

来源：https://github.com/junegunn/fzf/blob/master/README.md

### fzf + fd（更快的文件搜索）

export FZF_DEFAULT_COMMAND='fd --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND=""

# 自定义补全路径生成器
_fzf_compgen_path() {
  fd --hidden --follow --exclude ".git" . ""
}

### fzf + bat（文件预览）

export FZF_CTRL_T_OPTS="--preview 'bat -n --color=always {}'"

### fzf + ripgrep（全文搜索）

# 交互式全文搜索，结果用 vim 打开
rg --color=always --line-number --no-heading --smart-case "" |
  fzf --ansi       --delimiter :       --preview 'bat --color=always {1} --highlight-line {2}'       --preview-window 'up,60%,border-bottom,+{2}+3/3,~3'       --bind 'enter:become(vim {1} +{2})'

### fzf + git（checkout、log、diff）

# 安装 fzf-git.sh（强烈推荐）
git clone https://github.com/junegunn/fzf-git.sh
source fzf-git.sh/fzf-git.sh
# Ctrl-G + B: 分支选择
# Ctrl-G + H: commit log
# Ctrl-G + F: 文件

### 进程 kill

ps -ef | fzf | awk '{print }' | xargs kill -9

### FZF_DEFAULT_OPTS 配置

export FZF_DEFAULT_OPTS="
  --color=bg+:#3F3F3F,bg:#4B4B4B,border:#6B6B6B
  --color=hl:#719872,fg:#D9D9D9,header:#719872
  --color=info:#BDBB72,pointer:#E12672,marker:#E17899
  --height 40% --border
  --preview-window=right:50%
"

---

## 5. 终端复用器：2025 年选哪个

### 结论

| 场景 | 推荐 |
|------|------|
| AI 开发（本地为主）| tmux + tmux-resurrect |
| 想要好看 UI | Zellij |
| 轻度使用 | iTerm2 原生 |

### tmux 安装与配置

brew install tmux

# 安装 TPM（插件管理器）
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm

# 最小化 .tmux.conf
cat > ~/.tmux.conf << '''EOF'''
set -g @plugin '''tmux-plugins/tpm'''
set -g @plugin '''tmux-plugins/tmux-sensible'''
set -g @plugin '''tmux-plugins/tmux-resurrect'''
set -g @plugin '''tmux-plugins/tmux-continuum'''

set -g @continuum-restore '''on'''
set -g mouse on
set -g base-index 1
set -g default-terminal "screen-256color"

# prefix 改为 Ctrl-a（更顺手）
unbind C-b
set -g prefix C-a
bind C-a send-prefix

run '''~/.tmux/plugins/tpm/tpm'''
EOF

# 进入 tmux 后按 prefix + I 安装插件

**tmux-resurrect**：重启后恢复所有 session
https://github.com/tmux-plugins/tmux-resurrect

**tmux-continuum**：自动保存，开机自动恢复
https://github.com/tmux-plugins/tmux-continuum

### Zellij（2025 年值得关注）

brew install zellij
# 内置 UI，不需要记忆快捷键
# 适合新手，布局管理更直观
# https://zellij.dev

### iTerm2 原生（什么时候够用）

- 只在本地工作，不需要 SSH 持久化
- 使用 Arrangements 保存窗口布局：Window → Save Window Arrangement
- Session Restoration：https://iterm2.com/documentation-restoration.html

---

## 6. 现代 CLI 工具全景

### 一键安装清单

brew install bat eza fd ripgrep delta lazygit gh btop dust procs jq direnv zoxide httpie

### 文件操作

**bat**（cat 替代）
- 语法高亮 + 行号 + git 变更标记
- brew install bat
- alias cat='bat --paging=never'
- https://github.com/sharkdp/bat

**eza**（ls 替代，原 exa）
- 图标 + 颜色 + tree 模式 + git 状态
- brew install eza
- alias ls='eza'
- alias ll='eza -la --group-directories-first --icons'
- alias tree='eza --tree'
- https://github.com/eza-community/eza

**fd**（find 替代）
- 速度快，自动忽略 .gitignore
- brew install fd
- alias find='fd'
- https://github.com/sharkdp/fd

**ripgrep**（grep 替代）
- 比 grep 快 10x+，自动忽略 .git
- brew install ripgrep
- alias grep='rg'
- https://github.com/BurntSushi/ripgrep

### Git 工具

**delta**（git diff 替代）
- 语法高亮 diff，side-by-side 模式
- brew install delta

# 在 ~/.gitconfig 添加：
[core]
    pager = delta
[interactive]
    diffFilter = delta --color-only
[delta]
    navigate = true
    side-by-side = true
    line-numbers = true

- https://github.com/dandavison/delta
- 在线文档：https://dandavison.github.io/delta/

**lazygit**（TUI git 客户端）
- 可视化操作分支/commit/stash/rebase
- brew install lazygit
- alias lg='lazygit'
- GitHub Stars: 75k+
- https://github.com/jesseduffield/lazygit

**gh**（GitHub CLI）
- 终端管理 PR/Issue/Actions
- brew install gh
- gh pr create / gh pr status / gh issue list
- https://github.com/cli/cli

### 系统监控

**btop**（2025 年推荐，替代 htop）
- 现代 UI，GPU/磁盘/网络可视化
- brew install btop
- https://github.com/aristocratos/btop

**dust**（du 替代）
- 磁盘使用条形图可视化
- brew install dust
- https://github.com/bootandy/dust

### 开发工具

**jq**（JSON 处理，AI API 调用必备）
- brew install jq
- curl api.example.com | jq '.data[].id'
- https://github.com/stedolan/jq

**direnv**（自动加载 .env，AI 开发必备）
- 按目录自动管理 API KEY，不污染全局环境
- brew install direnv
- echo 'eval "
_direnv_hook() {
  trap -- '' SIGINT
  eval "$("/opt/homebrew/bin/direnv" export zsh)"
  trap - SIGINT
}
typeset -ag precmd_functions
if (( ! ${precmd_functions[(I)_direnv_hook]} )); then
  precmd_functions=(_direnv_hook $precmd_functions)
fi
typeset -ag chpwd_functions
if (( ! ${chpwd_functions[(I)_direnv_hook]} )); then
  chpwd_functions=(_direnv_hook $chpwd_functions)
fi"' >> ~/.zshrc
- 在项目目录创建 .envrc：export OPENAI_API_KEY=sk-...
- https://github.com/direnv/direnv

**zoxide**（z/autojump 替代）
- 智能记忆目录跳转
- brew install zoxide
- echo 'eval ""' >> ~/.zshrc
- 使用：z <关键词>
- https://github.com/ajeetdsouza/zoxide

---

## 7. 终端选择：2025 年

### 对比

| 终端 | 优势 | 劣势 |
|------|------|------|
| **Ghostty** | GPU 加速，原生 UI，速度最快 | 2024 底才发布 |
| **Warp** | AI 集成，Agent 功能 | 闭源，订阅制 |
| **iTerm2** | 功能最全，最稳定 | 较重 |
| **Alacritty** | 极简，GPU 加速 | 功能少 |
| **Kitty** | GPU 加速，可扩展 | 配置复杂 |

### Ghostty（2025 年最推荐）

- Mitchell Hashimoto（Vagrant/HashiCorp 创始人）2024 底发布
- 「fast, feature-rich, and cross-platform terminal emulator that uses platform-native UI and GPU acceleration」
- brew install --cask ghostty
- https://github.com/ghostty-org/ghostty

dwarvesf 的 dotfiles 已全面迁移到 Ghostty：
https://raw.githubusercontent.com/dwarvesf/dotfiles/master/README.md

---

## 8. Python/AI 环境管理：uv（2025 年标准答案）

### 为什么用 uv

- Rust 编写，比 pip 快 10-100x
- 替代 pyenv + pip + venv + poetry 全套
- 「An extremely fast Python package and project manager, written in Rust.」
- https://github.com/astral-sh/uv

### 安装

curl -LsSf https://astral.sh/uv/install.sh | sh
# 或
brew install uv

### 常用命令

uv init myproject          # 初始化项目
uv add numpy pandas        # 安装依赖（自动创建 venv）
uv run python script.py    # 在 venv 中运行
uv python install 3.12     # 安装 Python 版本
uv tool install ruff        # 安装全局工具

### 在 Starship 中显示虚拟环境

# starship.toml 已包含 [python] 模块，自动显示
# 显示格式：🐍 3.12.0 (myproject)

---

## 9. zsh 配置

### 插件管理：zinit（推荐）vs Oh My Zsh

| | Oh My Zsh | zinit |
|--|-----------|-------|
| 上手难度 | 简单 | 中等 |
| 启动速度 | 慢（1-3s） | 快（<100ms） |
| 插件数量 | 多 | 多 |
| 2025 推荐 | 初学者 | 有追求的用户 |

### zinit 安装

bash -c ""

### 推荐 .zshrc 结构（zinit 版）

# ~/.zshrc

# zinit
ZINIT_HOME="/Users/shenhuayu/.local/share/zinit/zinit.git"
[ ! -d  ] && mkdir -p ""
[ ! -d /.git ] && git clone https://github.com/zdharma-continuum/zinit.git ""
source "/zinit.zsh"

# 插件（lazy load）
zinit light zsh-users/zsh-autosuggestions
zinit light zsh-users/zsh-syntax-highlighting
zinit light Aloxaf/fzf-tab

# Prompt
eval ""

# 工具初始化
eval ""
eval ""
eval "
_direnv_hook() {
  trap -- '' SIGINT
  eval "$("/opt/homebrew/bin/direnv" export zsh)"
  trap - SIGINT
}
typeset -ag precmd_functions
if (( ! ${precmd_functions[(I)_direnv_hook]} )); then
  precmd_functions=(_direnv_hook $precmd_functions)
fi
typeset -ag chpwd_functions
if (( ! ${chpwd_functions[(I)_direnv_hook]} )); then
  chpwd_functions=(_direnv_hook $chpwd_functions)
fi"

# Alias
alias cat='bat --paging=never'
alias ls='eza'
alias ll='eza -la --group-directories-first --icons'
alias tree='eza --tree'
alias grep='rg'
alias find='fd'
alias lg='lazygit'
alias top='btop'

### 启动速度优化

# zsh 启动从 1.4s 降到 53ms 的案例
# https://dev.to/martin_oehlert/from-14s-to-53ms-optimizing-zsh-startup-on-macos-5f09
# 关键：zinit 的 lazy loading

---

## 10. ROI 排序（只装 10 个）

按「装了立刻感受到效率提升」排序：

1. **fzf** - 改变搜索方式，每天用 100 次
2. **uv** - Python 环境管理质变
3. **bat + eza + rg + fd** - 日常命令全面升级（算一组）
4. **Starship** - prompt 信息密度提升
5. **delta** - git diff 体验质变
6. **lazygit** - git 操作效率倍增
7. **direnv** - AI 开发 API KEY 管理
8. **zoxide** - 目录跳转质变
9. **Ghostty** - 终端速度提升
10. **tmux** - session 持久化，AI 工具必备

---

## 参考链接汇总

- Starship: https://github.com/starship/starship
- Powerlevel10k: https://github.com/romkatv/powerlevel10k
- Nerd Fonts: https://github.com/ryanoasis/nerd-fonts
- Catppuccin iTerm2: https://github.com/catppuccin/iterm
- fzf: https://github.com/junegunn/fzf
- fzf-git.sh: https://github.com/junegunn/fzf-git.sh
- tmux-resurrect: https://github.com/tmux-plugins/tmux-resurrect
- Zellij: https://zellij.dev
- bat: https://github.com/sharkdp/bat
- eza: https://github.com/eza-community/eza
- fd: https://github.com/sharkdp/fd
- ripgrep: https://github.com/BurntSushi/ripgrep
- delta: https://github.com/dandavison/delta
- lazygit: https://github.com/jesseduffield/lazygit
- btop: https://github.com/aristocratos/btop
- jq: https://github.com/stedolan/jq
- direnv: https://github.com/direnv/direnv
- zoxide: https://github.com/ajeetdsouza/zoxide
- uv: https://github.com/astral-sh/uv
- Ghostty: https://github.com/ghostty-org/ghostty
- zinit: https://github.com/zdharma-continuum/zinit
- Homebrew Bundle: https://docs.brew.sh/Brew-Bundle-and-Brewfile
- iTerm2 Color Schemes: https://iterm2colorschemes.com/
