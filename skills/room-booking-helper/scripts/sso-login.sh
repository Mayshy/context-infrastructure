#!/bin/bash

# 会议室预订助手 - SSO Cookie 获取 & 浏览器注入脚本
# 基于 CIBA 认证流程，通过 supabase 中间层完成 SSO 登录
#
# 用法: bash sso-login.sh <misId>
# 示例: bash sso-login.sh shiyunjing
#
# 流程:
#   1. CIBA 认证 → 获取 auth_req_id（用户需在大象上确认授权）
#   2. 轮询获取 access_token
#   3. 换票获取 calendar.sankuai.com 的 Cookie
#   4. 通过 CDP 注入 Cookie 到浏览器

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IDENTIFIER=$(bash "${SCRIPT_DIR}/read-env.sh")

# ===== 参数校验 =====
if [ -z "$1" ]; then
    echo "❌ 错误：请提供登录者 misId"
    echo ""
    echo "使用方式："
    echo "  bash $0 <misId>"
    echo ""
    echo "示例："
    echo "  bash $0 shiyunjing"
    exit 1
fi

LOGIN_HINT="$1"
BASE_URL="https://supabase.sankuai.com"
COOKIE_OUTPUT="${SCRIPT_DIR}/cookies.json"
COOKIE_JSON_OUTPUT="${SCRIPT_DIR}/../cookie.json"

# 检查 IDENTIFIER
if [[ "$IDENTIFIER" == ERROR* ]]; then
    echo "❌ IDENTIFIER 错误: $IDENTIFIER"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 开始 SSO 登录"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "login_hint: $LOGIN_HINT"
echo ""

# ===== 步骤 1：获取 auth_req_id =====
echo "📌 步骤 1：获取 auth_req_id（请在大象上确认授权）..."

BC_RESPONSE=$(curl --noproxy "*" -s -X POST "${BASE_URL}/api/sandbox/sso/ciba-auth" \
  -H 'Content-Type: application/json' \
  -d "{\"identifier\": \"${IDENTIFIER}\",\"misId\": \"${LOGIN_HINT}\"}")

echo "响应: $BC_RESPONSE"

AUTH_REQ_ID=$(echo "$BC_RESPONSE" | python3 -c "
import json,sys
data=json.load(sys.stdin)
d=data.get('data',{}) if data.get('code')==0 else {}
print(d.get('authReqId','') or d.get('existingAuthReqId',''))
" 2>/dev/null)

if [ -z "$AUTH_REQ_ID" ]; then
    ERROR_DESC=$(echo "$BC_RESPONSE" | python3 -c "
import json,sys
data=json.load(sys.stdin)
print(data.get('data',{}).get('errorDescription','') or data.get('message','未知错误'))
" 2>/dev/null)
    echo "❌ auth_req_id 获取失败: $ERROR_DESC"
    exit 1
fi

echo "✅ auth_req_id: $AUTH_REQ_ID"
echo ""

# ===== 步骤 2：轮询获取 access_token =====
echo "📌 步骤 2：轮询获取 access_token（每 5s 一次，最多 3 分钟）..."

MAX_RETRY=36
RETRY=0
ACCESS_TOKEN=""

while [ $RETRY -lt $MAX_RETRY ]; do
    RETRY=$((RETRY + 1))
    echo "  第 ${RETRY}/${MAX_RETRY} 次轮询..."

    TOKEN_RESPONSE=$(curl --noproxy "*" -s -X POST "${BASE_URL}/api/sandbox/sso/ciba-token" \
      -H 'Content-Type: application/json' \
      -d "{\"authReqId\": \"${AUTH_REQ_ID}\"}")

    ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "
import json,sys
data=json.load(sys.stdin)
print(data.get('data',{}).get('accessToken','') if data.get('code')==0 else '')
" 2>/dev/null)

    if [ -n "$ACCESS_TOKEN" ]; then
        echo "✅ access_token 获取成功"
        break
    fi

    sleep 5
done

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ 轮询超时，未获取到 access_token"
    exit 1
fi

echo ""

# ===== 步骤 3：换票 =====
echo "📌 步骤 3：换票获取 Cookie..."

EXCHANGE_RESPONSE=$(curl --noproxy "*" -s -X POST "${BASE_URL}/api/sandbox/sso/exchange-token" \
  -H 'Content-Type: application/json' \
  -d "{\"accessToken\": \"${ACCESS_TOKEN}\",\"domain\": \"calendar.sankuai.com\"}")

COOKIE_DATA=$(echo "$EXCHANGE_RESPONSE" | python3 -c "
import json,sys
data=json.load(sys.stdin)
print(json.dumps(data.get('data',[])) if data.get('data') else '')
" 2>/dev/null)

if [ -z "$COOKIE_DATA" ] || [ "$COOKIE_DATA" = "[]" ] || [ "$COOKIE_DATA" = "null" ]; then
    ERROR_MSG=$(echo "$EXCHANGE_RESPONSE" | python3 -c "
import json,sys
data=json.load(sys.stdin)
print(data.get('message','未知错误'))
" 2>/dev/null)
    echo "❌ 换票失败: $ERROR_MSG"
    exit 1
fi

echo "✅ 换票成功"
echo ""

# ===== 步骤 4：保存 cookies.json（CDP 注入用） =====
echo "📌 步骤 4：保存 Cookie..."

python3 - << PYEOF
import json

exchange_response = '''${EXCHANGE_RESPONSE}'''
output_path = "${COOKIE_OUTPUT}"
cookie_json_path = "${COOKIE_JSON_OUTPUT}"

try:
    data = json.loads(exchange_response)
    cookie_data = data.get('data', [])

    if not cookie_data:
        print("❌ 无法获取 cookie 数据")
        exit(1)

    # 保存 CDP 注入用的 cookies.json
    with open(output_path, 'w') as f:
        json.dump(cookie_data, f, indent=2, ensure_ascii=False)
    print(f"✅ cookies.json 已保存: {output_path}")

    # 同时生成 cookie.json（拼接为字符串，供 Python requests 使用）
    cookie_str = '; '.join(f"{c['name']}={c['value']}" for c in cookie_data)
    cookie_json = {
        'cookie': cookie_str,
        'mis': '${LOGIN_HINT}',
    }
    with open(cookie_json_path, 'w') as f:
        json.dump(cookie_json, f, indent=2, ensure_ascii=False)
    print(f"✅ cookie.json 已保存: {cookie_json_path}")

except Exception as e:
    print(f"❌ 保存失败: {e}")
    exit(1)
PYEOF

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""

# ===== 步骤 5：注入 Cookie 到浏览器 =====
echo "📌 步骤 5：注入 Cookie 到浏览器..."

python3 "${SCRIPT_DIR}/inject-cookie.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 完成！Cookie 已注入浏览器"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
