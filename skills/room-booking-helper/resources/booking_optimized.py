#!/usr/bin/env python3
"""
优化版会议室预订脚本 - 支持本地缓存

功能:
  - 使用本地缓存减少 API 调用
  - 第一次运行时获取并缓存城市、建筑、楼层
  - 第一次运行时获取并缓存其他条件列表
  - 后续运行时直接使用缓存数据
  - 支持清除缓存命令
"""

import json
import urllib.request
import ssl
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 导入缓存管理器
sys.path.insert(0, str(Path(__file__).parent))
from cache_manager import CacheManager

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

cache_manager = CacheManager()

# 读取 Cookie 和用户信息
with open('/Users/wangjun/.catpaw/sso_config.json', 'r') as f:
    config = json.load(f)
    cookie_string = config['ssoid']
    mis_id = config.get('misId', 'wangjun137')

def make_request(url, headers=None, data=None, method='POST'):
    """发送 HTTP 请求"""
    if headers is None:
        headers = {}
    
    default_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Request-Source': 'OpenClaw-Agent',
        'M-UserContext': 'eyJsb2NhbGUiOiJ6aCIsInRpbWVab25lIjoiQXNpYS9TaGFuZ2hhaSJ9',
        'Cookie': cookie_string
    }
    default_headers.update(headers)
    
    if data:
        data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=default_headers, method=method)
    
    try:
        with urllib.request.urlopen(req, context=ssl_context) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.fp:
            try:
                return json.loads(e.fp.read().decode('utf-8'))
            except:
                return {"error": str(e)}
        raise

def get_buildings_data():
    """获取城市、建筑、楼层列表 (优先使用缓存)"""
    
    # 检查缓存
    cached_data = cache_manager.get_buildings_cache()
    if cached_data:
        print("📦 使用缓存的建筑数据")
        return cached_data
    
    print("🌐 从 API 获取建筑数据...")
    response = make_request('https://calendar.sankuai.com/meeting/api/pc/room/appointment/findCityBuildingAndFloor')
    
    if response.get('code') == 200:
        data = response.get('data', [])
        # 保存到缓存
        if cache_manager.save_buildings_cache(data):
            print("✅ 建筑数据已缓存")
        return data
    else:
        print(f"❌ 获取建筑数据失败: {response}")
        return None

def get_conditions_data():
    """获取其他条件列表 (优先使用缓存)"""
    
    # 检查缓存
    cached_data = cache_manager.get_conditions_cache()
    if cached_data:
        print("📦 使用缓存的条件数据")
        return cached_data
    
    print("🌐 从 API 获取条件数据...")
    response = make_request('https://calendar.sankuai.com/room/front/pc/room/moreInfo', method='GET')
    
    if response.get('code') == 200 or response.get('data'):
        data = response.get('data', response)
        # 保存到缓存
        if cache_manager.save_conditions_cache(data):
            print("✅ 条件数据已缓存")
        return data
    else:
        print(f"⚠️  获取条件数据失败，继续处理: {response}")
        # 条件数据不必要，继续处理
        return {}

def add_room_monitor(building_id, floor_ids, start_time_ms, end_time_ms, head_count):
    """
    添加空闲会议室监测预约任务
    
    参数:
      building_id: 建筑ID
      floor_ids: 楼层ID列表
      start_time_ms: 开始时间戳（毫秒）
      end_time_ms: 结束时间戳（毫秒）
      head_count: 人数
    
    返回:
      成功返回 True，失败返回 False
    """
    print(f"\n主动为您添加空闲监测任务...")
    
    monitor_data = {
        "buildingId": building_id,
        "planStartTimestamp": start_time_ms,
        "planEndTimestamp": end_time_ms,
        "floorIds": floor_ids if floor_ids else [],
        "headCount": head_count
    }
    
    headers = {
        'sec-ch-ua-platform': 'macOS',
        'Referer': 'https://calendar.sankuai.com/rooms',
        'tz': 'Asia/Shanghai',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?0',
        'X-Requested-With': 'XMLHttpRequest',
        'la': 'zh',
        'M-UserContext': 'eyJsb2NhbGUiOiJ6aCIsInRpbWVab25lIjoiQXNpYS9TaGFuZ2hhaSJ9'
    }
    
    try:
        monitor_response = make_request(
            'https://calendar.sankuai.com/room/front/appointment-room/insertV2',
            headers=headers,
            data=monitor_data
        )
        
        if monitor_response.get('code') == 200:
            message = monitor_response.get('data', '添加成功')
            print(f"✅ 已为您添加监测任务")
            print(f"   {message}")
            return True
        else:
            print(f"⚠️  添加监测任务失败: {monitor_response.get('message', '未知错误')}")
            return False
    except Exception as e:
        print(f"⚠️  添加监测任务异常: {str(e)}")
        return False

def book_room(city_name, building_name, date_str, start_time, end_time, capacity=5):
    """
    预订会议室
    
    参数:
      city_name: 城市名称 (如 "上海市")
      building_name: 建筑名称 (如 "互联D2栋")
      date_str: 日期字符串 (如 "2026-03-05" 或 "明天")
      start_time: 开始时间 (如 "19:00")
      end_time: 结束时间 (如 "20:00")
      capacity: 容量要求 (默认 5 人)
    """
    
    print(f"\n{'='*60}")
    print(f"开始预订流程")
    print(f"{'='*60}")
    print(f"城市: {city_name}")
    print(f"建筑: {building_name}")
    print(f"日期: {date_str}")
    print(f"时间: {start_time}-{end_time}")
    print(f"容量: {capacity}人")
    print(f"{'='*60}\n")
    
    # 步骤 1: 获取建筑数据
    print("步骤 1: 获取建筑数据...")
    buildings_response = get_buildings_data()
    if not buildings_response:
        print("❌ 无法获取建筑数据")
        return False
    
    # 步骤 2: 查找指定城市和建筑
    print(f"\n步骤 2: 查找 {city_name} - {building_name}...")
    city_data = None
    for city in buildings_response:
        if city_name in city.get('cityName', ''):
            city_data = city
            break
    
    if not city_data:
        print(f"❌ 未找到 {city_name}")
        print("可用城市:")
        for city in buildings_response:
            print(f"  - {city.get('cityName')}")
        return False
    
    building_id = None
    building_name_full = None
    for building_floor in city_data['buildingAndFloorVoList']:
        building = building_floor['building']
        if building_name in building['name']:
            building_id = building['id']
            building_name_full = building['name']
            break
    
    if not building_id:
        print(f"❌ 未找到 {building_name} 的建筑")
        print(f"可用建筑 ({city_name}):")
        for building_floor in city_data['buildingAndFloorVoList']:
            print(f"  - {building_floor['building']['name']} (ID: {building_floor['building']['id']})")
        return False
    
    print(f"✅ 找到建筑: {building_name_full} (ID: {building_id})")
    
    # 步骤 3: 处理日期
    print(f"\n步骤 3: 处理日期...")
    if date_str.lower() == "明天":
        tomorrow = datetime.now(timezone(timedelta(hours=8))) + timedelta(days=1)
    else:
        tomorrow = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone(timedelta(hours=8)))
    
    tomorrow_date = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp_ms = int(tomorrow_date.timestamp() * 1000)
    print(f"✅ 查询日期: {tomorrow.strftime('%Y-%m-%d')}")
    
    # 步骤 4: 获取条件数据 (可选)
    print(f"\n步骤 4: 获取条件数据...")
    conditions_data = get_conditions_data()
    
    # 步骤 5: 查询会议室
    print(f"\n步骤 5: 查询 {start_time}-{end_time} 的会议室...")
    search_data = {
        "date": timestamp_ms,
        "buildingId": str(building_id),
        "floorIds": [],
        "capacity": [{"capacityMin": 1, "capacityMax": 100, "name": "全部"}],
        "startTime": start_time,
        "endTime": end_time
    }
    
    rooms_response = make_request(
        'https://calendar.sankuai.com/meeting/api/pc/room/appointment/v2/find-rooms',
        data=search_data
    )
    
    if not rooms_response.get('data'):
        print(f"❌ 查询会议室失败: {rooms_response}")
        return False
    
    rooms = rooms_response['data']
    print(f"✅ 找到 {len(rooms)} 个会议室")
    
    # 步骤 6: 查询预订情况
    print(f"\n步骤 6: 查询预订情况...")
    room_ids = [room['id'] for room in rooms]
    appointments_data = {
        "date": timestamp_ms,
        "roomIds": room_ids
    }
    
    appointments_response = make_request(
        'https://calendar.sankuai.com/meeting/api/pc/room/appointment/findRoomAppointmentsV2',
        data=appointments_data
    )
    
    # 查找空闲会议室
    booked_room_ids = set()
    start_time_parts = start_time.split(':')
    end_time_parts = end_time.split(':')
    start_offset_ms = (int(start_time_parts[0]) * 3600 + int(start_time_parts[1]) * 60) * 1000
    end_offset_ms = (int(end_time_parts[0]) * 3600 + int(end_time_parts[1]) * 60) * 1000
    
    for apt_item in appointments_response.get('data', []):
        for apt in apt_item.get('appointmentVOS', []):
            apt_start = apt['startTime'] - timestamp_ms
            apt_end = apt['endTime'] - timestamp_ms
            # 检查时间是否重叠
            if apt_start < end_offset_ms and apt_end > start_offset_ms:
                booked_room_ids.add(apt_item['roomId'])
    
    # 找出空闲的会议室
    available_rooms = [room for room in rooms if room['id'] not in booked_room_ids]
    
    if not available_rooms:
        print(f"❌ {start_time}-{end_time} 没有空闲会议室")
        print(f"预订情况: {len(booked_room_ids)} 个房间已被预订")
        
        # 未找到空闲会议室时，主动添加监测任务
        print(f"\n正在为您自动添加空闲监测...")
        
        # 获取楼层IDs
        floor_ids = []
        for building_floor in city_data['buildingAndFloorVoList']:
            if building_floor['building']['id'] == building_id:
                for floor in building_floor.get('floors', []):
                    floor_ids.append(floor['id'])
                break
        
        # 计算时间戳
        start_time_ms = timestamp_ms + start_offset_ms
        end_time_ms = timestamp_ms + end_offset_ms
        
        # 添加监测任务
        monitor_success = add_room_monitor(
            building_id=building_id,
            floor_ids=floor_ids,
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms,
            head_count=capacity
        )
        
        return monitor_success
    
    print(f"✅ 找到 {len(available_rooms)} 个空闲会议室")
    
    # 步骤 7: 选择会议室
    print(f"\n步骤 7: 选择会议室...")
    selected_room = available_rooms[0]
    print(f"✅ 选择房间: {selected_room['name']} (ID: {selected_room['id']}, 容量: {selected_room['capacity']})")
    
    # 步骤 8: 获取用户 empId
    print(f"\n步骤 8: 获取用户员工 ID...")
    account_response = make_request(
        'https://calendar.sankuai.com/api/v2/xm/meeting/dataset/account',
        data={"filter": mis_id}
    )
    
    emp_id = None
    if account_response.get('data'):
        for user in account_response['data']:
            if user.get('mis') == mis_id:
                emp_id = user.get('empId')
                break
    
    if not emp_id:
        print(f"❌ 获取员工 ID 失败")
        return False
    
    print(f"✅ 员工 ID: {emp_id}")
    
    # 步骤 9: 提交预订
    print(f"\n步骤 9: 提交预订...")
    start_time_ms = timestamp_ms + start_offset_ms
    end_time_ms = timestamp_ms + end_offset_ms
    
    booking_data = {
        "title": "会议",
        "startTime": start_time_ms,
        "endTime": end_time_ms,
        "isAllDay": 0,
        "location": "",
        "attendees": [emp_id],
        "noticeType": 0,
        "noticeRule": "P0Y0M0DT0H10M0S",
        "recurrencePattern": {
            "type": "NONE",
            "showType": "NONE"
        },
        "deadline": 0,
        "memo": "",
        "organizer": emp_id,
        "room": {
            "id": selected_room['id'],
            "name": selected_room['name'],
            "email": selected_room.get('email', ''),
            "capacity": selected_room['capacity'],
            "floorId": selected_room.get('floorId', 0),
            "floorName": selected_room.get('floorName', ''),
            "buildingId": building_id,
            "buildingName": building_name_full
        },
        "appKey": "meeting",
        "bookType": 11
    }
    
    booking_response = make_request(
        'https://calendar.sankuai.com/api/v2/xm/schedules',
        data=booking_data
    )
    
    if booking_response.get('message') == '成功' or booking_response.get('code') == 200:
        print(f"\n{'='*60}")
        print(f"✅ 预订成功！")
        print(f"{'='*60}")
        print(f"\n预订详情:")
        print(f"  会议室: {selected_room['name']}")
        print(f"  日期: {tomorrow.strftime('%Y-%m-%d')}")
        print(f"  时间: {start_time}-{end_time}")
        print(f"  容量: {selected_room['capacity']}人")
        print(f"  地点: {building_name_full}")
        print(f"\n{'='*60}\n")
        return True
    else:
        print(f"❌ 预订失败")
        print(f"响应: {json.dumps(booking_response, ensure_ascii=False, indent=2)}")
        return False


if __name__ == '__main__':
    # 示例: 预订上海互联D2栋明天19-20点的会议室
    success = book_room(
        city_name="上海",
        building_name="D2",
        date_str="明天",
        start_time="19:00",
        end_time="20:00",
        capacity=5
    )
    
    sys.exit(0 if success else 1)
