#!/bin/bash

set -e

echo "🚀 OpenCode 美团代理配置脚本"
echo "================================"
echo ""

# 检查依赖
echo "📋 检查依赖..."

if ! command -v jq &> /dev/null; then
    echo "❌ jq 未安装"
    echo "请运行: brew install jq"
    exit 1
fi
echo "✅ jq 已安装"

if ! command -v opencode &> /dev/null; then
    echo "❌ opencode 未安装"
    echo "请访问 https://opencode.ai 安装"
    exit 1
fi
echo "✅ opencode 已安装"

if ! command -v mc &> /dev/null; then
    echo "❌ mc 未安装"
    exit 1
fi
echo "✅ mc 已安装"

echo ""

# 检查 mc --code 是否运行
echo "🔍 检查 mc --code 状态..."
if ! pgrep -f "mc --code" > /dev/null; then
    echo "⚠️  mc --code 未运行"
    echo "请在另一个终端运行: mc --code"
    echo ""
    read -p "启动 mc --code 后按回车继续..."
fi

# 获取 token
echo "🔑 获取认证 token..."

# 尝试从配置文件读取
CONFIG_FILE=~/.config/mcopilot-cli/.config.yaml
if [ -f "$CONFIG_FILE" ]; then
    MEITUAN_TOKEN=$(grep "AUTHORIZATION:" "$CONFIG_FILE" | awk '{print $2}')
fi

# 如果配置文件没有，尝试从环境变量
if [ -z "$MEITUAN_TOKEN" ]; then
    MEITUAN_TOKEN=$(ps eww $(pgrep -f "mc --code" | head -1) 2>/dev/null | tr ' ' '\n' | grep ANTHROPIC_AUTH_TOKEN | cut -d= -f2)
fi

if [ -z "$MEITUAN_TOKEN" ]; then
    echo "❌ 无法获取 token"
    echo "请检查:"
    echo "  1. mc --code 是否在运行"
    echo "  2. ~/.config/mcopilot-cli/.config.yaml 是否存在"
    exit 1
fi
echo "✅ Token 获取成功: ${MEITUAN_TOKEN:0:8}..."

# 安装 Anthropic SDK
echo ""
echo "📦 安装 @ai-sdk/anthropic..."
cd ~/.config/opencode
if npm list @ai-sdk/anthropic &> /dev/null; then
    echo "✅ @ai-sdk/anthropic 已安装"
else
    npm install @ai-sdk/anthropic
    echo "✅ @ai-sdk/anthropic 安装完成"
fi

# 检查配置文件
echo ""
echo "⚙️  配置 OpenCode..."

CONFIG_FILE=~/.config/opencode/opencode.json

# 检查是否已有 meituan provider
if grep -q '"meituan"' "$CONFIG_FILE"; then
    echo "✅ meituan provider 已存在，更新配置..."
    # 更新现有配置
    jq --arg token "$MEITUAN_TOKEN" \
       '.provider.meituan.options.apiKey = $token' \
       "$CONFIG_FILE" > /tmp/opencode-config.json
    mv /tmp/opencode-config.json "$CONFIG_FILE"
else
    echo "➕ 添加 meituan provider..."
    # 添加新配置
    jq --arg token "$MEITUAN_TOKEN" \
       '.provider.meituan = {
          "npm": "@ai-sdk/anthropic",
          "name": "Meituan Claude Proxy",
          "options": {
            "baseURL": "https://mcli.sankuai.com/v1",
            "apiKey": $token,
            "headers": {
              "X-Working-Dir": "/placeholder/working/dir"
            }
          },
          "models": {
            "claude-sonnet-4-6": {
              "name": "claude-sonnet-4-6",
              "limit": {
                "context": 200000,
                "output": 8192
              }
            },
            "claude-opus-4-6": {
              "name": "claude-opus-4-6",
              "limit": {
                "context": 200000,
                "output": 8192
              }
            },
            "claude-haiku-4-5": {
              "name": "claude-haiku-4-5",
              "limit": {
                "context": 200000,
                "output": 8192
              }
            }
          }
        }' \
       "$CONFIG_FILE" > /tmp/opencode-config.json
    mv /tmp/opencode-config.json "$CONFIG_FILE"
fi

# 创建包装脚本
echo ""
echo "📝 创建包装脚本..."

mkdir -p ~/.local/bin

cat > ~/.local/bin/opencode-mt << 'EOF'
#!/bin/bash

# 获取当前工作目录
WORKING_DIR=$(pwd)

# 检查 mc --code 是否在运行
if ! pgrep -f "mc --code" > /dev/null; then
    echo "Error: mc --code is not running. Please start it first with: mc --code"
    exit 1
fi

# 从配置文件获取 token
CONFIG_FILE=~/.config/mcopilot-cli/.config.yaml
if [ -f "$CONFIG_FILE" ]; then
    CURRENT_TOKEN=$(grep "AUTHORIZATION:" "$CONFIG_FILE" | awk '{print $2}')
fi

# 如果配置文件没有，尝试从环境变量
if [ -z "$CURRENT_TOKEN" ]; then
    CURRENT_TOKEN=$(ps eww $(pgrep -f "mc --code" | head -1) 2>/dev/null | tr ' ' '\n' | grep ANTHROPIC_AUTH_TOKEN | cut -d= -f2)
fi

if [ -z "$CURRENT_TOKEN" ]; then
    echo "Error: Could not get token from mc --code process or config file"
    echo "Please check:"
    echo "  1. mc --code is running"
    echo "  2. ~/.config/mcopilot-cli/.config.yaml exists"
    exit 1
fi

# 临时配置文件
TEMP_CONFIG="/tmp/opencode-mt-$$.json"

# 更新配置文件 (更新工作目录和 token)
jq --arg dir "$WORKING_DIR" --arg token "$CURRENT_TOKEN" \
   '.provider.meituan.options.headers."X-Working-Dir" = $dir |
    .provider.meituan.options.apiKey = $token' \
   ~/.config/opencode/opencode.json > "$TEMP_CONFIG"

# 临时替换配置文件
ORIGINAL_CONFIG=~/.config/opencode/opencode.json
mv "$ORIGINAL_CONFIG" "$ORIGINAL_CONFIG.backup"
mv "$TEMP_CONFIG" "$ORIGINAL_CONFIG"

# 运行 opencode
opencode -m meituan/claude-sonnet-4-6 "$@"
EXIT_CODE=$?

# 恢复原配置
mv "$ORIGINAL_CONFIG.backup" "$ORIGINAL_CONFIG"

exit $EXIT_CODE
EOF

chmod +x ~/.local/bin/opencode-mt
echo "✅ 包装脚本创建完成: ~/.local/bin/opencode-mt"

# 检查 PATH
echo ""
echo "🔍 检查 PATH 配置..."
if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
    echo "✅ ~/.local/bin 已在 PATH 中"
else
    echo "➕ 添加 ~/.local/bin 到 PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    echo "✅ 已添加到 ~/.zshrc，请运行: source ~/.zshrc"
fi

# 验证配置
echo ""
echo "✅ 配置完成！"
echo ""
echo "📋 验证配置:"
opencode models meituan

echo ""
echo "🎉 设置完成！"
echo ""
echo "使用方法:"
echo "  1. 确保 mc --code 在运行"
echo "  2. cd /path/to/your/project"
echo "  3. opencode-mt run \"hello\""
echo "  4. 或直接运行: opencode-mt"
echo ""
echo "创建别名 (可选):"
echo "  echo 'alias omt=\"opencode-mt\"' >> ~/.zshrc"
echo "  source ~/.zshrc"
echo ""
