"""
美团会议室预订助手 - SSO 登录 & Cookie 自动获取工具

使用方法：
    python3 login.py

功能：
    1. 弹出浏览器窗口，引导用户完成 SSO 登录
    2. 登录成功后自动提取并保存 Cookie 到 ~/.catpaw/skills/room-booking-helper/cookie.json
    3. 验证 Cookie 有效性

依赖安装：
    pip3 install playwright
    python3 -m playwright install chromium
"""
import asyncio
import json
import os
import shutil
import ssl
import urllib.request
from playwright.async_api import async_playwright

# 临时 Chrome profile 目录
TMP_PROFILE_DIR = '/tmp/pw_calendar_profile'
# Chrome 可执行文件路径（macOS）
CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
# Cookie 持久化存储路径
COOKIE_SAVE_PATH = os.path.join(os.path.dirname(__file__), 'cookie.json')

RESULT = {}


async def _login_and_capture():
    """启动浏览器，等待用户登录，自动提取 Cookie"""
    async with async_playwright() as p:
        print("=" * 50)
        print("🌐 正在启动浏览器...")
        print("   请在弹出的窗口中完成美团 SSO 登录")
        print("   登录成功后程序将自动提取 Cookie，无需其他操作")
        print("=" * 50)

        context = await p.chromium.launch_persistent_context(
            user_data_dir=TMP_PROFILE_DIR,
            executable_path=CHROME_PATH,
            headless=False,
            args=['--no-first-run', '--no-default-browser-check'],
        )

        page = await context.new_page()

        # 拦截 userinfo 接口请求，直接从请求头获取 Cookie
        async def on_request(request):
            if 'userinfo' in request.url and 'sankuai' in request.url:
                headers = request.headers
                cookie = headers.get('cookie', '')
                access_token = headers.get('access-token', '')
                if cookie and len(cookie) > 100:
                    RESULT['cookie'] = cookie
                    RESULT['access_token'] = access_token
                    print("✅ 已从请求头自动捕获 Cookie")

        page.on('request', on_request)

        # 打开日历页
        try:
            await page.goto('https://calendar.sankuai.com/rooms',
                            wait_until='domcontentloaded', timeout=60000)
        except Exception as e:
            print(f"   页面加载提示: {e}")

        # 等待登录完成，最多 3 分钟
        print("⏳ 等待登录完成（最多3分钟）...")
        for i in range(180):
            if RESULT.get('cookie'):
                break
            await asyncio.sleep(1)
            if (i + 1) % 30 == 0:
                print(f"   仍在等待... {i + 1}s")
            # 已登录成功后主动触发 userinfo 接口
            if 'calendar.sankuai.com/rooms' in page.url and i > 10 and not RESULT.get('cookie'):
                try:
                    await page.evaluate(
                        "fetch('/api/v2/xm/userinfo', {credentials: 'include'})"
                    )
                except Exception:
                    pass

        # 兜底：直接从 browser context 读取 Cookie
        if not RESULT.get('cookie'):
            print("   尝试从 browser context 提取 Cookie...")
            cookies = await context.cookies(['https://calendar.sankuai.com'])
            if cookies:
                cookie_str = '; '.join(f"{c['name']}={c['value']}" for c in cookies)
                access_token = next(
                    (c['value'] for c in cookies if c['name'] == 'scheduleWeb_accessToken'), ''
                )
                RESULT['cookie'] = cookie_str
                RESULT['access_token'] = access_token
                print(f"✅ 从 context 提取到 {len(cookies)} 个 Cookie")

        await context.close()


def _verify_cookie(cookie, access_token):
    """验证 Cookie 有效性，返回用户信息"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    headers = {
        'Cookie': cookie,
        'access-token': access_token,
        'M-UserContext': 'eyJsb2NhbGUiOiJ6aCIsInRpbWVab25lIjoiQXNpYS9TaGFuZ2hhaSJ9',
        'X-Requested-With': 'XMLHttpRequest',
        'tz': 'Asia/Shanghai',
        'la': 'zh',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://calendar.sankuai.com/rooms',
    }
    req = urllib.request.Request(
        'https://calendar.sankuai.com/api/v2/xm/userinfo', headers=headers
    )
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode())
    return data.get('data', {})


def load_cookie():
    """读取已保存的 Cookie，如果不存在则返回 None"""
    if os.path.exists(COOKIE_SAVE_PATH):
        with open(COOKIE_SAVE_PATH, 'r') as f:
            return json.load(f)
    return None


def main():
    # 检查是否已有有效 Cookie
    existing = load_cookie()
    if existing:
        print("🔍 检测到已保存的 Cookie，验证中...")
        try:
            user = _verify_cookie(existing['cookie'], existing['access_token'])
            if user.get('empId'):
                print(f"✅ Cookie 仍有效：{user.get('name')}（empId: {user.get('empId')}）")
                print(f"   无需重新登录，Cookie 文件：{COOKIE_SAVE_PATH}")
                return
        except Exception:
            print("   已保存的 Cookie 已过期，需要重新登录...")

    # 清理旧的临时 profile，重新登录
    if os.path.exists(TMP_PROFILE_DIR):
        shutil.rmtree(TMP_PROFILE_DIR)
    os.makedirs(TMP_PROFILE_DIR)

    asyncio.run(_login_and_capture())

    if RESULT.get('cookie'):
        # 验证并保存
        try:
            user = _verify_cookie(RESULT['cookie'], RESULT['access_token'])
            save_data = {
                'cookie': RESULT['cookie'],
                'access_token': RESULT['access_token'],
                'emp_id': user.get('empId', ''),
                'name': user.get('name', ''),
                'mis': user.get('mis', ''),
            }
            with open(COOKIE_SAVE_PATH, 'w') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            print("\n" + "=" * 50)
            print(f"🎉 登录成功！")
            print(f"   用户：{user.get('name')}（empId: {user.get('empId')}）")
            print(f"   Cookie 已保存到：{COOKIE_SAVE_PATH}")
            print("=" * 50)
        except Exception as e:
            print(f"❌ 验证失败: {e}")
    else:
        print("❌ 未能获取 Cookie，请重试")


if __name__ == '__main__':
    main()

