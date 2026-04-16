#!/usr/bin/env python3
"""
一体化快速会议室预订脚本

用法:
  python quick_book.py --city 上海 --building D2 --date 2026-03-10 --start 12:00 --end 13:00 [--capacity 5] [--mis wangjun137]

特点:
  - 单次执行完成全流程（查建筑→查房间→查预订→预订，一气呵成）
  - 优先使用本地缓存定位建筑
  - 批量尝试预订，遇到成功立即返回
  - 自动处理已下线会议室
  - 全部失败时自动创建监测任务
"""

import json
import argparse
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import requests as req_lib
    USE_REQUESTS = True
except ImportError:
    import urllib.request
    import ssl
    USE_REQUESTS = False
    _ssl_ctx = ssl.create_default_context()
    _ssl_ctx.check_hostname = False
    _ssl_ctx.verify_mode = ssl.CERT_NONE

SKILL_DIR = Path(__file__).parent.parent
COOKIE_FILE = SKILL_DIR / 'cookie.json'
CACHE_FILE = SKILL_DIR / 'resources' / 'cache' / 'buildings_cache.json'
TZ = timezone(timedelta(hours=8))
OFFLINE_THRESHOLD_MS = 20 * 60 * 60 * 1000

# ── helpers ────────────────────────────────────────────────

def load_cookie():
    with open(COOKIE_FILE) as f:
        d = json.load(f)
    return d['cookie'], d.get('mis', '')

def headers(cookie, extra=None):
    h = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Request-Source': 'OpenClaw-Agent',
        'M-UserContext': 'eyJsb2NhbGUiOiJ6aCIsInRpbWVab25lIjoiQXNpYS9TaGFuZ2hhaSJ9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Cookie': cookie
    }
    if extra:
        h.update(extra)
    return h

def api(url, hdrs, data=None, method='POST'):
    if USE_REQUESTS:
        r = req_lib.post(url, headers=hdrs, json=data, timeout=30) if method == 'POST' else req_lib.get(url, headers=hdrs, timeout=30)
        return r.json()
    body = json.dumps(data).encode() if data else None
    rq = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    with urllib.request.urlopen(rq, context=_ssl_ctx, timeout=30) as rp:
        return json.loads(rp.read().decode())

def cap_range(n):
    for lo, hi, name in [(1,6,"1-6人"),(7,14,"7-14人"),(15,21,"15-21人"),(22,40,"22-40人"),(41,60,"41-60人"),(61,200,"61+人")]:
        if lo <= n <= hi:
            return {"capacityMin": lo, "capacityMax": hi, "name": name}
    return {"capacityMin": 1, "capacityMax": 6, "name": "1-6人"}

# ── building lookup ────────────────────────────────────────

def find_building(city_kw, bld_kw):
    """从缓存查找建筑，返回 (id, fullName, floorIds, err)"""
    if not CACHE_FILE.exists():
        return None, None, None, "no_cache"
    with open(CACHE_FILE) as f:
        cache = json.load(f)
    for city in cache.get('data', {}).get('cityList', []):
        if city_kw in city.get('cityName', ''):
            for b in city.get('buildings', []):
                if bld_kw in b.get('buildingName', ''):
                    fids = [fl['floorId'] for fl in b.get('floors', [])]
                    return b['buildingId'], b['buildingName'], fids, None
            avail = [b['buildingName'] for b in city.get('buildings', [])]
            return None, None, None, f"城市{city['cityName']}内未匹配建筑'{bld_kw}'，可选: {avail}"
    return None, None, None, f"未找到城市'{city_kw}'"

def fetch_and_cache_buildings(hdrs):
    """从 API 获取建筑列表并缓存（兼容两种 API 返回格式）"""
    resp = api('https://calendar.sankuai.com/room/front/app/room/cityBuilding', hdrs, {})
    if resp.get('code') != 200:
        return False
    cache = {"cached_at": int(datetime.now().timestamp()*1000), "data": {"cityList": []}}
    for c in resp.get('data', []):
        co = {"cityId": c['code'], "cityName": c['name'], "buildings": []}
        for b in c.get('children', []):
            bo = {"buildingId": b['code'], "buildingName": b['name'], "floors": []}
            for f in b.get('children', []):
                bo['floors'].append({"floorId": f['code'], "floorName": f['name']})
            co['buildings'].append(bo)
        cache['data']['cityList'].append(co)
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, ensure_ascii=False)
    return True

# ── main flow ──────────────────────────────────────────────

def quick_book(city, building, date_str, start_time, end_time, capacity=5, mis_id=None):
    """
    一体化快速预订。
    返回 (success, message, details_dict)
    """
    # 1. cookie
    cookie, default_mis = load_cookie()
    mis_id = mis_id or default_mis
    hdrs = headers(cookie)

    # 2. 定位建筑
    bid, bname, fids, err = find_building(city, building)
    if err:
        if err == "no_cache":
            print("📦 缓存不存在，从 API 获取建筑列表...")
        else:
            print(f"⚠️ {err}，重新获取...")
        if not fetch_and_cache_buildings(hdrs):
            return False, "获取建筑列表失败", {}
        bid, bname, fids, err = find_building(city, building)
        if err:
            return False, err, {}

    print(f"✅ 建筑: {bname} (ID:{bid})")

    # 3. 时间计算
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=TZ)
    date_ts = int(dt.timestamp() * 1000)
    sh, sm = map(int, start_time.split(':'))
    eh, em = map(int, end_time.split(':'))
    start_ts = int(dt.replace(hour=sh, minute=sm).timestamp() * 1000)
    end_ts   = int(dt.replace(hour=eh, minute=em).timestamp() * 1000)

    # 4. 查会议室
    rooms = api(
        'https://calendar.sankuai.com/meeting/api/pc/room/appointment/v2/find-rooms',
        hdrs, {"date": date_ts, "buildingId": str(bid), "floorIds": [], "capacity": [cap_range(capacity)], "startTime": start_time, "endTime": end_time}
    ).get('data', [])
    if not rooms:
        return False, f"无符合条件的会议室 ({cap_range(capacity)['name']})", {}
    print(f"✅ 候选: {len(rooms)} 个")

    # 5. 查预订 → 筛选空闲
    rmap = {r['id']: r for r in rooms}
    appt = api(
        'https://calendar.sankuai.com/meeting/api/pc/room/appointment/findRoomAppointmentsV2',
        hdrs, {"date": date_ts, "roomIds": list(rmap.keys())}
    )
    free, busy, offline = [], 0, 0
    for ra in appt.get('data', []):
        rid = ra['roomId']
        apts = ra.get('appointmentVOS') or []
        if any((a['endTime']-a['startTime']) > OFFLINE_THRESHOLD_MS for a in apts):
            offline += 1; continue
        if any(a['startTime'] < end_ts and a['endTime'] > start_ts for a in apts):
            busy += 1; continue
        free.append(rmap[rid])
    print(f"✅ 空闲:{len(free)} 占用:{busy} 下线:{offline}")

    if not free:
        return _create_monitor(hdrs, cookie, bid, fids, start_ts, end_ts, capacity)

    # 6. empId
    acct = api('https://calendar.sankuai.com/api/v2/xm/meeting/dataset/account', hdrs, {"filter": mis_id})
    eid = None
    for u in acct.get('data', []):
        if u.get('mis') == mis_id:
            eid = str(u['empId']); break
    if not eid and acct.get('data'):
        eid = str(acct['data'][0]['empId'])
    if not eid:
        return False, f"未找到 {mis_id} 的 empId", {}

    # 7. 批量尝试预订
    for rm in free:
        body = {
            "title": f"{mis_id}的会议",
            "startTime": start_ts, "endTime": end_ts, "isAllDay": 0,
            "location": "", "attendees": [eid],
            "noticeType": 0, "noticeRule": "P0Y0M0DT0H10M0S",
            "recurrencePattern": {"type":"NONE","showType":"NONE"},
            "deadline": 0, "memo": "", "organizer": eid,
            "room": {
                "id": rm['id'], "name": rm['name'], "email": rm.get('email',''),
                "capacity": rm.get('capacity',5), "disabled": 0,
                "floorId": rm.get('floorId',0), "floorName": rm.get('floorName',''),
                "buildingId": bid, "buildingName": bname
            },
            "appKey": "meeting", "bookType": 11
        }
        try:
            r = api('https://calendar.sankuai.com/api/v2/xm/schedules', hdrs, body)
            if r.get('code') == 200 or r.get('message') == '成功':
                sid = r.get('data',{}).get('scheduleId') if isinstance(r.get('data'), dict) else r.get('data')
                return True, "预订成功", {
                    "room": rm['name'], "floor": rm.get('floorName',''),
                    "capacity": rm.get('capacity',5), "building": bname,
                    "date": date_str, "time": f"{start_time}-{end_time}",
                    "schedule_id": sid
                }
            msg = r.get('data',{}).get('message','') if isinstance(r.get('data'),dict) else r.get('message','')
            if '同时预订' in str(msg):
                return False, f"同时段预订超限: {msg}", {}
            print(f"  ⚠️ {rm['name']}: {msg}")
        except Exception as e:
            print(f"  ⚠️ {rm['name']}: {e}")

    return _create_monitor(hdrs, cookie, bid, fids, start_ts, end_ts, capacity)

def _create_monitor(hdrs, cookie, bid, fids, start_ts, end_ts, cap):
    mh = {**headers(cookie, {'Referer':'https://calendar.sankuai.com/rooms','tz':'Asia/Shanghai','la':'zh'})}
    try:
        mr = api('https://calendar.sankuai.com/room/front/appointment-room/insertV2', mh,
                 {"buildingId":bid,"planStartTimestamp":start_ts,"planEndTimestamp":end_ts,"floorIds":fids or [],"headCount":cap})
        if mr.get('code') == 200:
            return False, f"无空闲会议室，已创建监测: {mr.get('data')}", {"monitor":True}
        if mr.get('code') == 50801:
            return False, "无空闲会议室，该时段已有监测任务", {"monitor":True}
        return False, f"无空闲，监测创建失败: {mr.get('message')}", {}
    except Exception as e:
        return False, f"无空闲，监测异常: {e}", {}

# ── CLI ────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description='快速预订会议室')
    p.add_argument('--city', required=True)
    p.add_argument('--building', required=True)
    p.add_argument('--date', required=True, help='YYYY-MM-DD')
    p.add_argument('--start', required=True, help='HH:MM')
    p.add_argument('--end', required=True, help='HH:MM')
    p.add_argument('--capacity', type=int, default=5)
    p.add_argument('--mis', help='MIS账号')
    a = p.parse_args()

    ok, msg, det = quick_book(a.city, a.building, a.date, a.start, a.end, a.capacity, a.mis)

    print(f"\n{'='*50}")
    if ok:
        print("✅ 预订成功！")
        for k in ['room','floor','capacity','building','date','time','schedule_id']:
            if det.get(k): print(f"  {k}: {det[k]}")
    else:
        print(f"❌ {msg}")
    print('='*50)
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
