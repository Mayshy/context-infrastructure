#!/bin/bash

# CatPaw Cookie 获取脚本
# 用法: bash get-catpaw-cookie.sh <misId>
# 返回: 直接输出 cookie 字符串（如：1d47d6ff96_ssoid=xxx）

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IDENTIFIER=$(bash "${SCRIPT_DIR}/read-env.sh")

# ===== 配置 =====
if [ -z "$1" ]; then
    echo "❌ 错误：请提供登录者 misId"
    echo ""
    echo "使用方式："
    echo "  bash $0 <misId>"
    echo ""
    echo "示例："
    echo "  bash $0 qigaoxiang"
    exit 1
fi
LOGIN_HINT="$1"
BASE_URL="https://supabase.sankuai.com"

# 检查 IDENTIFIER 是否以 ERROR 开头
if [[ "$IDENTIFIER" == ERROR* ]]; then
    echo "❌  IDENTIFIER 错误: $IDENTIFIER"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀  开始获取 Token"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "login_hint: $LOGIN_HINT"
echo ""

# ===== 步骤 1：获取 auth_req_id =====
echo "📌  步骤 1：获取 auth_req_id..."

BC_RESPONSE=$(curl --noproxy "*" -s -X POST "${BASE_URL}/api/sandbox/sso/ciba-auth" \
  -H 'Content-Type: application/json' \
  -d "{\"identifier\": \"${IDENTIFIER}\",\"misId\": \"${LOGIN_HINT}\"}")

echo "响应: $BC_RESPONSE"

# 解析响应（优先从 authReqId 获取，如果没有则从 existingAuthReqId 获取）
AUTH_REQ_ID=$(echo "$BC_RESPONSE" | python3 -c "import json,sys; data=json.load(sys.stdin); d=data.get('data',{}) if data.get('code')==0 else {}; print(d.get('authReqId','') or d.get('existingAuthReqId',''))" 2>/dev/null)

if [ -z "$AUTH_REQ_ID" ]; then
    ERROR_DESC=$(echo "$BC_RESPONSE" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('data',{}).get('errorDescription','') or data.get('message','未知错误'))" 2>/dev/null)
    echo "❌  auth_req_id 获取失败: $ERROR_DESC"
    exit 1
fi

echo "✅  auth_req_id: $AUTH_REQ_ID"
echo ""

# ===== 步骤 2：轮询获取 access_token =====
echo "📌  步骤 2：轮询获取 access_token（每 5s 一次，最多 3 分钟）..."

MAX_RETRY=36
RETRY=0
ACCESS_TOKEN=""

while [ $RETRY -lt $MAX_RETRY ]; do
    RETRY=$((RETRY + 1))
    echo "  第 ${RETRY}/${MAX_RETRY} 次轮询..."

    TOKEN_RESPONSE=$(curl --noproxy "*" -s -X POST "${BASE_URL}/api/sandbox/sso/ciba-token" \
      -H 'Content-Type: application/json' \
      -d "{\"authReqId\": \"${AUTH_REQ_ID}\"}")

    echo "  响应: ${TOKEN_RESPONSE:0:100}..."

    ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('data',{}).get('accessToken','') if data.get('code')==0 else '')" 2>/dev/null)
    
    if [ -n "$ACCESS_TOKEN" ]; then
        echo "✅  access_token 获取成功"
        break
    fi

    # 检查是否有错误
    ERROR_DESC=$(echo "$TOKEN_RESPONSE" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('data',{}).get('errorDescription','') or data.get('message','未知错误'))" 2>/dev/null)
    if [ -n "$ERROR_DESC" ] && [ "$ERROR_DESC" != "null" ]; then
        echo "  错误: $ERROR_DESC"
    fi

    echo "  等待 5s..."
    sleep 5
done

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌  轮询超时，未获取到 access_token"
    exit 1
fi

echo ""

# ===== 步骤 3：换票获取 cookie =====

EXCHANGE_RESPONSE=$(curl --noproxy "*" -s -X POST "${BASE_URL}/api/sandbox/sso/exchange-token-by-client-ids" \
  -H 'Content-Type: application/json' \
  -d "{\"accessToken\": \"${ACCESS_TOKEN}\",\"clientIds\": [\"5a7dd523f0\", \"2f73f89b68\"]}")

echo "响应: $EXCHANGE_RESPONSE"

# 检查响应中的 data 字段
COOKIE_DATA=$(echo "$EXCHANGE_RESPONSE" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('data','') if data.get('data') else '')" 2>/dev/null)

if [ -z "$COOKIE_DATA" ] || [ "$COOKIE_DATA" = "[]" ] || [ "$COOKIE_DATA" = "null" ]; then
    ERROR_MSG=$(echo "$EXCHANGE_RESPONSE" | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('message','未知错误'))" 2>/dev/null)
    echo "❌  换票失败: $ERROR_MSG"
    exit 1
fi

echo "✅  换票成功"
echo ""

# ===== 步骤 4：返回 cookie =====
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅  Token 获取完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 将 cookie 数据转换为字符串格式，并添加前缀
CATPAW_COOKIE="1d47d6ff96_ssoid=$COOKIE_DATA"

# 直接输出 cookie，供其他脚本捕获
echo "$CATPAW_COOKIE"
