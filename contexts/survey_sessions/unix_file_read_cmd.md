# Unix 快速读/看文件命令速查

> 适用场景：日常文件浏览、代码查阅、日志分析、快速编辑  
> 假设环境：macOS / Linux，主流工具已安装（ripgrep、bat 等可选）

---

## 1. less — 翻页阅读（最推荐）

**场景**：中等大小文本文件的交互式阅读，不占用编辑器资源。

```bash
less file.txt          # 打开
less -N file.txt       # 显示行号
less -S file.txt       # 超出宽度截断（不折行）
less +/pattern file    # 启动时跳到匹配处
```

| 按键 | 动作 |
| --- | --- |
| `j` / `k` 或 `↓` / `↑` | 下一行 / 上一行 |
| `Space` / `PageDown` | 下一页 |
| `b` / `PageUp` | 上一页 |
| `g` | 跳到第一行 |
| `G` | 跳到最后一行 |
| `/pattern` | 向下搜索 |
| `?pattern` | 向上搜索 |
| `n` / `N` | 下一个 / 上一个匹配 |
| `&pattern` | 只显示匹配行（再 `&` 恢复）|
| `q` | 退出 |
| `=` | 显示当前行号和文件信息 |
| `h` | 帮助 |

```bash
# 常用组合
dmesg | less -S          # 系统日志，截断长行
cat large.log | less     # 大文件分页
history | less           # 命令历史
```

---

## 2. more — 简单翻页

**场景**：功能弱，但最小化恢复环境（Rescue Mode）里必定存在。

```bash
more file.txt
```

| 按键 | 动作 |
| --- | --- |
| `Space` / `b` | 下翻 / 上翻 |
| `Enter` | 下一行 |
| `/pattern` | 搜索 |
| `q` | 退出 |

> 能用 `less` 就别用 `more`。

---

## 3. cat — 输出整个文件

**场景**：小文件全览、合并文件、重定向输入。

```bash
cat file.txt                        # 打印全部
cat -n file.txt                    # 显示行号（含空行）
cat -b file.txt                    # 显示行号（不含空行）
tac file.txt                       # 倒序输出（从尾巴看起）
cat file1.txt file2.txt > merged.txt  # 合并
```

> ⚠️ 不要用 `cat` 读大文件——会刷屏且无交互能力。

---

## 4. head / tail — 看头 / 看尾

**场景**：日志分析、配置文件头部/尾部检查。

```bash
# head：看开头
head file.txt              # 默认前10行
head -n 20 file.txt        # 前20行
head -c 200 file.txt       # 前200字节

# tail：看结尾
tail file.txt              # 默认后10行
tail -n 20 file.txt       # 后20行
tail -f /var/log/syslog   # 实时跟踪（Ctrl+C 退出）
tail -f access.log | rg 404   # 实时过滤
```

---

## 5. grep — 文件内搜索

**场景**：在文件或目录中搜索特定字符串。

```bash
# 基础
grep "error" file.log
grep -n "error" file.log          # 显示行号
grep -i "error" file.log          # 不区分大小写
grep -r "error" ./dir/             # 递归搜索目录
grep -r -l "error" ./dir/         # 只显示文件名
grep -c "error" file.log          # 计数出现次数
grep -v "info" file.log           # 反选（排除匹配行）
grep -A2 -B3 "error" file.log    # 显示匹配行+上下文

# 正则
grep "^Start" file.txt            # 行首匹配
grep -E "error|warning" file.log  # OR 多个模式
grep -P "\d{4}-\d{2}-\d{2}" log  # Perl 正则
```

---

## 6. ripgrep (rg) — 现代 grep 替代

**场景**：大型代码库搜索，比 grep 快一个数量级。

```bash
rg "pattern"                       # 当前目录递归
rg -n "pattern" file.py            # 显示行号
rg -C3 "pattern" file.py           # 上下文3行
rg --type py "pattern"              # 只搜 Python 文件
rg -g "*.md" "pattern"             # 只搜 md 文件
rg -l "pattern"                    # 只显示文件名
rg -w "pattern"                    # 整词匹配
rg -v "pattern"                    # 反选
```

> 安装：`brew install ripgrep`

---

## 7. find / fd — 查找文件

```bash
# find：通用但语法繁琐
find . -name "*.log"
find . -type f -name "*.txt"
find . -type d -name "node_modules"
find . -mtime -7 -name "*.py"          # 7天内修改
find . -size +100M                        # 大于100MB
find . -name "*.py" -exec grep "pattern" {} \;

# fd：更快，语法更直觉
fd "\.py$"                   # 找所有 Python 文件
fd -H "secret" .             # 含隐藏文件
fd -e py -e js "main"       # 多种扩展名
fd -p "^start"               # 按正则
```

> fd 安装：`brew install fd`

---

## 8. bat — 现代 cat 替代

**场景**：取代 `cat`，支持语法高亮、自动分页、Git 标注。

```bash
bat file.txt                  # 带高亮显示
bat -n file.txt               # 显示行号
bat -p file.txt              # 无装饰输出（纯内容）
bat -l go file.go             # 指定语言
bat --map "*.conf=>ini" f.conf
bat -n --highlight-line 42 file.txt  # 高亮指定行
```

> 安装：`brew install bat`

```bash
# 对比
cat file.txt     # 原始输出，无高亮
bat file.txt     # 高亮 + 行号 + 自动分页（大于一屏时）
```

---

## 9. vim — 全功能编辑器（只读查看模式）

**场景**：需要精确跳转、跨文件搜索、复杂导航。

```bash
vim file.txt         # 打开编辑
view file.txt        # 只读模式打开（防止误修改）

# 启动后快捷键
/pattern             # 向下搜索
?pattern             # 向上搜索
n / N               # 下一个 / 上一个匹配
:set nu              # 显示行号
:set hlsearch        # 高亮搜索结果
gg                  # 跳到文件开头
G                   # 跳到文件末尾
:20                 # 跳到第20行
Ctrl+d              # 下翻半页
Ctrl+u              # 上翻半页
zz                  # 当前行居中
*                   # 高亮当前词并跳到下一个
#                   # 高亮当前词并跳到上一个

# 退出
:q     # 退出（未修改）
:q!    # 强制退出
:wq    # 保存退出
:x     # 同上，简写
```

---

## 10. nano — 极简编辑器

**场景**：临时编辑一两行，不需要学习成本。

```bash
nano file.txt
```

| 快捷键 | 动作 |
| --- | --- |
| `Ctrl+O` | 保存 |
| `Ctrl+W` | 搜索 |
| `Ctrl+K` / `Ctrl+U` | 剪切 / 粘贴整行 |
| `Ctrl+Y` / `Ctrl+V` | 上翻页 / 下翻页 |
| `Ctrl+X` | 退出 |

---

## 11. sed / awk — 行处理

### sed（替换、选行）

```bash
sed -n '10,20p' file.txt          # 打印第10-20行
sed 's/old/new/g' file.txt        # 全局替换
sed -i 's/old/new/g' file.txt    # 直接修改文件
sed '/pattern/d' file.txt          # 删除匹配行
sed '5d' file.txt                  # 删除第5行
```

### awk（字段处理）

```bash
awk '{print $1, $3}' file.txt          # 打印第1和第3列
awk -F',' '{print $2}' file.csv         # 以逗号为分隔符
awk 'NR>1 && $3>100' file.txt          # 跳过表头，筛选第3列>100
awk -F: '{print $1}' /etc/passwd        # 按 : 分隔，打印第1列
```

---

## 12. wc — 统计行 / 词 / 字符

```bash
wc -l file.txt     # 行数（最常用）
wc -w file.txt     # 词数
wc -c file.txt     # 字节数
```

---

## 场景速查表

| 场景 | 推荐命令 |
| --- | --- |
| 临时查看小文件 | `cat` 或 `bat` |
| 交互式读大文件 | `less` 或 `bat` |
| 只看文件头部 | `head` |
| 实时跟踪日志 | `tail -f` |
| 搜索文件内容 | `rg` 或 `grep -r` |
| 查找文件 | `fd` 或 `find` |
| 编辑文件 | `vim` |
| 临时轻量编辑 | `nano` |
| 行处理 / 统计 | `awk` / `sed` |
| 合并文件 | `cat f1 f2 > merged` |
| 快速计数 | `wc -l` |

---

## 推荐工具链

日常使用建议安装以下工具，效率提升显著：

| 工具 | 替代 | 安装 |
| --- | --- | --- |
| `bat` | `cat` | `brew install bat` |
| `rg` | `grep` | `brew install ripgrep` |
| `fd` | `find` | `brew install fd` |
| `eza` | `ls` | `brew install eza` |
| `fzf` | 交互式搜索 | `brew install fzf` |
