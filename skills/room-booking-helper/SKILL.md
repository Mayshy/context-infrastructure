---
name: room-booking-helper
description: 美团会议室预订助手。支持按日期、时间、地点、人数筛选可用会议室，自动查询已预订时段，找到空闲会议室后直接提交预订。用户提出订会议室、预约会议室、找会议室、安排会议地点、确认某时段是否有空会议室时使用。
---

# 美团会议室预订助手

### 三步开始预订会议室

**第1步：SSO 登录获取 Cookie** — 通过 CIBA 认证自动完成（用户在大象上确认授权即可）

**第2步：提供预订信息**
```
告诉我：帮我订一个[城市][地点]明天[时间]的会议室，[人数]个人
```

**第3步：完成预订**
```
我会自动查询、分析、预订，然后告诉你结果
```

**就这么简单！** 🎉

### 使用示例
- ✅ "帮我订一个北京保利广场西座明天上午10-11点的会议室，5个人"
- ✅ "查一下上海互联D2栋下午14-15点有没有空会议室"  
- ✅ "我需要一个容纳15人的会议室，成都科技园，后天下午"

---


## ⚠️ 调用频率限制（重要）

为避免对会议室系统造成压力，**请遵守以下频率限制**：

| 操作 | 建议频率 | 说明 |
|------|----------|------|
| 预订请求 | **≤ 1次/10秒** | 提交预订接口（schedules） |
| 查询请求 | **≤ 1次/秒** | 查会议室、查预订等读操作 |
| SSO 登录 | **按需** | Cookie 有效期约 2-4 小时，过期再登录 |

**禁止行为**：
- ❌ 循环轮询会议室状态
- ❌ 批量预订多个会议室囤积
- ❌ 短时间内重复预订-取消操作

**AI 请求标识**：
所有 API 请求都携带 `X-Request-Source: OpenClaw-Agent` header，便于服务端识别和监控。

---

## 🔐 SSO 登录（CIBA 认证）

本 Skill 集成了 CIBA（Client Initiated Backchannel Authentication）认证流程，无需用户手动扫码或提供密码。

### 认证流程

1. **发起 CIBA 认证** → 用户在大象上收到授权确认请求
2. **用户点击确认** → 系统自动获取 access_token
3. **换票** → 用 access_token 换取 calendar.sankuai.com 的 Cookie
4. **注入浏览器** → 通过 CDP 注入 Cookie，后续页面操作和浏览器内 fetch 自动携带认证

### 使用方式

```bash
# 自动化 SSO 登录（需要用户 misId）
bash ~/.openclaw/skills/room-booking-helper/scripts/sso-login.sh <misId>

# 示例
bash ~/.openclaw/skills/room-booking-helper/scripts/sso-login.sh shiyunjing
```

### 脚本说明

| 文件 | 说明 |
|------|------|
| `scripts/sso-login.sh` | CIBA 认证主脚本：获取 token → 换票 → 注入浏览器 |
| `scripts/inject-cookie.py` | 通过 CDP 将 Cookie 注入 Chromium 浏览器 |
| `scripts/read-env.sh` | 读取 sandbox identifier（CIBA 认证必需） |

### 产出文件

| 文件 | 用途 |
|------|------|
| `scripts/cookies.json` | Cookie 数组格式（CDP 注入用） |
| `cookie.json` | Cookie 字符串格式（Python requests 备用） |

### 判断是否需要登录

以下任一条件成立即需要执行 SSO 登录：
- 浏览器访问 `calendar.sankuai.com` 时被 SSO 拦截
- URL 包含 `ssosv`、`sso.sankuai.com`、`passport.sankuai.com`
- 页面出现二维码扫码界面
- API 调用返回 401 或 "未登录"

### Agent 调用示例

```python
# Agent 在需要登录时执行：
exec("bash ~/.openclaw/skills/room-booking-helper/scripts/sso-login.sh shiyunjing", timeout=200)
# 提示用户在大象上确认授权
# 登录完成后刷新页面或直接用浏览器 fetch 调用 API
```

---

## 🚀 新增优化功能 - 本地缓存

为了提升预订速度，本 Skill 现已支持**本地缓存优化**功能：

### ✨ 缓存优化特性

| 功能 | 说明 |
|------|------|
| **自动缓存** | 首次获取城市/建筑/楼层数据后自动缓存 |
| **智能使用** | 后续预订自动使用缓存，无需重新获取 |
| **性能提升** | 预订速度提快 40%（缓存命中时） |
| **自动过期** | 缓存 7 天后自动过期，确保数据新鲜 |
| **手动清除** | 支持命令行手动清除缓存 |

### 📊 缓存文件位置

```
~/.catpaw/skills/room-booking-helper/resources/cache/
├── buildings_cache.json      (建筑数据缓存, ~788KB)
└── conditions_cache.json     (查询条件缓存, ~1KB)
```

## 美团内网 SSO 登录与 Cookie 获取
所有美团内部网站（*.sankuai.com）共享同一套 SSO 登录机制。必须先通过 browser use 完成登录并获取 Cookie，后续查询与预订全部通过 API 调用完成。

### 判断是否需要登录
以下任一条件成立即表示未登录，需要走 SSO 流程：

URL 包含 ssosv、sso.sankuai.com、passport.sankuai.com
页面出现二维码扫码界面
页面无目标站点的核心业务元素（如会议室页面的时间轴、会议室列表）
SSO 扫码登录流程
通过 browser use 打开 https://calendar.sankuai.com/rooms。
保持登录页可见，等待二维码加载完成。
明确提示用户："请使用手机扫码登录"。
轮询页面状态（间隔 2-3 秒）；检测到 URL 不再包含 SSO 关键词且出现目标站点业务元素后继续。
若等待超时（>60s）或二维码失效，刷新页面并提示用户重试。
禁止：不要要求用户提供账号密码或验证码，仅支持扫码登录。 若登录后仍无法进入会议室列表，立即告知失败原因并询问是否改为仅做信息整理（不提交）。
### 登录后获取 Cookie
SSO 登录成功后，立即通过 browser use 在页面内执行 JS 获取 Cookie：
document.cookie
将获取到的 Cookie 字符串保存到会话中，后续所有 API 调用都携带此 Cookie。

重要：仅 SSO 登录环节使用 browser use 自动化操作页面；查询与预订优先通过 **浏览器内 fetch**（`evaluate` 执行 JS fetch）完成，这样可以复用浏览器的 SSO session，无需单独管理 Cookie。只有在浏览器不可用时才降级为 Python requests + cookie.json。

## API 调用方式优先级（重要！）

**首选：浏览器内 fetch**（推荐，速度最快）
```javascript
// 通过 browser use 的 evaluate 执行，自动携带浏览器 Cookie
fetch(url, {method:'POST', headers:{...}, credentials:'include', body:JSON.stringify(payload)})
  .then(r => r.json()).then(d => JSON.stringify(d))
```
优点：自动携带 SSO Cookie，无需读取/管理 cookie.json，认证最可靠。

**备选：Python requests + cookie.json**
仅在浏览器不可用时使用。从 `~/.catpaw/skills/room-booking-helper/cookie.json` 读取 cookie 字段。

# **缓存内容说明**：
- **buildings_cache.json**：城市、建筑、楼层列表数据
  - 实际数据结构：`{cached_at, data: {cityList: [{cityId, cityName, buildings: [{buildingId, buildingName, floors: [{floorId, floorName}]}]}]}}`
  - 大小：约 500KB
  - 更新频率：建筑新增或调整时需要更新
  
- **conditions_cache.json**：会议室查询条件数据
  - 包含：设备列表(equips)、容量范围(capacity)、窗户选项(window)
  - 大小：约 1KB
  - 更新频率：很少变化，基本固定

### 🔧 缓存管理命令

```bash
# 查看缓存状态
python ~/.catpaw/skills/room-booking-helper/resources/manage_cache.py status

# 清除所有缓存
python ~/.catpaw/skills/room-booking-helper/resources/manage_cache.py clear-all

# 清除建筑缓存
python ~/.catpaw/skills/room-booking-helper/resources/manage_cache.py clear-buildings

# 清除条件缓存
python ~/.catpaw/skills/room-booking-helper/resources/manage_cache.py clear-conditions
```

### 💡 使用提示

- **第一次预订**：会从 API 获取数据并自动缓存（速度稍慢，但只需一次）
- **后续预订**：直接使用缓存数据（速度快 40%）
- **缓存过期**：7 天后自动失效，下次使用时重新获取
- **强制更新**：使用上述清除命令即可立即重新获取最新数据

---

## 快速开始

会议室预订流程分为三步：

1. **收集预订信息**：城市、大厦、楼层、日期、时间段、人数
2. **查询空闲会议室**：根据条件检索符合的会议室和其预订状态（支持本地缓存优化）
3. **提交预订**：找到空闲会议室后自动提交
4. **如果没有空闲的会议室** 则创建个空闲预约的任务


## 信息收集流程

### 收集策略

依序收集以下信息（每次只问一个问题）：

| 参数 | 是否必填 | 说明 | 示例 |
|------|----------|------|------|
| 城市 | 必填 | 用户输入城市名称 | 北京、上海、成都 |
| 园区/大楼 | 必填 | 从下拉列表中选择 | 北京/保利广场西座 |
| 楼层 | 可选 | 不指定则标记为"不限楼层" | 2层、3层 |
| 日期 | 必填 | 具体日期 | 2026-02-18 |
| 时间段 | 必填 | 开始和结束时间 | 10:00-12:00 |
| 人数 | 可选 | 默认5人 | 5、10、15 |

### 默认值策略

用户未指定时，应用以下默认值并**提示用户确认**：

- **日期**：今天
- **开始时间**：当前时间 + 2小时，向上取整到最近半点
- **时长**：60分钟
- **人数**：5人
- **楼层**：不限楼层

### 预订规则（必须遵守）

在收集信息阶段即校验以下规则，不符合时立即告知用户：

#### 1. 预订窗口限制
- 每日 9:30 开放未来 8 个自然日内的预订权限
- ❌ 超过 8 天 → 提示不可预订，建议调整日期

#### 2. 次数限制
- 同一账号每天每间会议室最多可预订 3 次

#### 3. 时长限制
- 单次会议可预订时长：**15 分钟 ~ 240 分钟（4 小时）**
- ❌ 超出范围 → 建议拆分或调整

#### 4. 历史时间不可预订
- 当前时间以前的时间段不可预订
- ❌ 早于当前时间 → 立即提示并要求重新填写

#### 5. 查询时间范围限制
- API 仅支持查询**历史 7 天内**的会议室数据
- 超过 7 天的请求会返回 `"仅支持历史7天内的数据查询"` 错误
- 对于超过 7 天的预订，需要提示用户调整日期范围

## 空闲会议室查询流程

### 步骤 1：获取城市、大厦和楼层列表

调用接口：`POST https://calendar.sankuai.com/room/front/app/room/cityBuilding`

**请求头**：必须携带浏览器当前 Cookie 保持登录状态

**接口特点**：
- 使用 POST 方法，无需请求体
- 返回数据结构为 JSON 数组，包含所有城市及其关联的建筑和楼层
- 数据采用树形结构，通过 `children` 字段组织层级关系

**返回数据示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "code": 3531,
      "name": "北京市",
      "type": "city",
      "children": [
        {
          "code": 843,
          "name": "北京/保利广场西座",
          "type": "building",
          "children": [
            {
              "code": 2001,
              "name": "2层",
              "type": "floor"
            },
            {
              "code": 2002,
              "name": "3层",
              "type": "floor"
            }
          ]
        }
      ]
    },
    {
      "code": 3532,
      "name": "上海市",
      "type": "city",
      "children": [
        {
          "code": 335,
          "name": "上海/互联D2栋",
          "type": "building",
          "children": [
            {
              "code": 1068,
              "name": "5层",
              "type": "floor"
            }
          ]
        }
      ]
    }
  ]
}
```

**⚠️ 重要提示**：
- **响应码是 200 而非 1**
- **data 是数组，不是对象**
- 字段名称使用 `code` (而非 `cityId`/`buildingId`)、`name` (而非 `cityName`/`buildingName`)
- 结构采用 `children` 字段 (而非 `buildings`/`floors`)

从返回结果中提取用户选择的城市、大厦、楼层对应的 code ID。

#### 💡 使用缓存优化（推荐）

建筑列表数据相对稳定，强烈建议使用缓存：

```python
from cache_manager import CacheManager
import requests

cache_manager = CacheManager()

# 1. 优先从缓存读取
cached_data = cache_manager.get_buildings_cache()

if cached_data:
    print("✅ 从缓存读取建筑列表")
    buildings = cached_data
else:
    print("⏳ 缓存未命中，从API获取...")
    url = 'https://calendar.sankuai.com/room/front/app/room/cityBuilding'
    response = requests.post(url, headers=headers)
    result = response.json()
    
    if result.get('code') == 200:
        buildings = result.get('data', [])  # 注意：data 是数组
        # 保存到缓存
        cache_manager.save_buildings_cache(buildings)
        print("✅ 已保存到缓存")

# 2. 查找目标城市和建筑
for city in buildings:
    if '上海' in city['name']:  # 使用 'name' 而非 'cityName'
        for building in city['children']:  # 使用 'children' 而非 'buildings'
            if building['code'] == 335:  # 使用 'code' 而非 'buildingId'
                print(f"找到: {building['name']}")
                floors = building['children']  # 使用 'children' 而非 'floors'
                # 使用楼层数据...
```

#### ⚠️ 重要：建筑数据结构说明

**数据结构层级**：
```
data
└── cityList (数组)
    └── cityId + cityName (城市)
        └── buildings (数组)
            ├── buildingId (建筑ID，全局唯一)
            ├── buildingName (建筑名称，格式："城市/建筑名")
            └── floors (楼层数组)
                ├── floorId (楼层ID)
                └── floorName (楼层名称)
```

**关键注意事项** ⚠️：

1. **buildingId 是全局唯一的**
   - 每个建筑ID在整个系统中唯一标识一个建筑
   - 不同城市的建筑绝不会有相同的ID
   - 例如：
     - `buildingId = 335` → `上海/互联D2栋` (上海市)
     - `buildingId = 843` → `北京/保利广场西座` (北京市)

2. **必须通过城市上下文确认建筑**
   - 不能仅凭建筑名称中的关键词（如"D2"）进行匹配
   - 必须先确定城市，再在该城市的 `buildings` 中查找
   - 查找流程：
     ```python
     # 正确做法
     city_list = data.get('data', {}).get('cityList', [])
     for city in city_list:
         if '上海' in city['cityName']:  # 1. 先定位城市
             for building in city['buildings']:
                 if 'D2' in building['buildingName']:  # 2. 再匹配建筑名
                     building_id = building['buildingId']
                     # 找到正确的建筑
     ```

3. **查询后必须验证返回的建筑名称**
   - 在调用会议室查询接口后，检查返回的 `room.buildingName`
   - 确认实际地点与用户需求一致
   - 如果不一致，说明使用了错误的 buildingId

4. **缓存数据结构**
   - 如果使用缓存，缓存的 JSON 结构应保持与 API 返回一致
   - 缓存文件应包含完整的城市→建筑→楼层层级关系
   - 示例缓存结构：
     ```json
     {
       "timestamp": 1709567890000,
       "data": {
         "cityList": [
           {
             "cityId": 3532,
             "cityName": "上海市",
             "buildings": [...]
           }
         ]
       }
     }
     ```

**常见错误案例**：

❌ **错误做法**：直接在所有建筑中搜索关键词
```python
# 错误：可能匹配到其他城市的相似建筑
city_list = data.get('data', {}).get('cityList', [])
for city in city_list:
    for building in city['buildings']:
        if 'D2' in building['buildingName']:
            selected_building = building
            break
```

✅ **正确做法**：先定位城市，再查找建筑
```python
# 正确：确保在正确的城市中查找
city_list = data.get('data', {}).get('cityList', [])
target_city = None
for city in city_list:
    if '上海' in city['cityName']:
        target_city = city
        break

if target_city:
    for building in target_city['buildings']:
        if 'D2' in building['buildingName']:
            selected_building = building
            # 进一步验证：
            print(f"确认建筑: {building['buildingName']} (ID: {building['buildingId']})")
```

### 步骤 2：查询其他条件列表

调用接口：`POST https://calendar.sankuai.com/room/front/pc/room/moreInfo`

**返回结构包含**：
- **equips**：可用设备列表（Zoom、腾讯会议、投影等）
- **capacity**：容量范围选项（1-6人、7-14人、15-21人等）
- **window**：窗户选项（有窗/无窗）

**返回数据示例**：
```json
{
  "status": 1,
  "data": {
    "equips": [
      {"id": 1, "name": "Zoom"},
      {"id": 2, "name": "腾讯会议"},
      {"id": 3, "name": "投影仪"}
    ],
    "capacity": [
      {"capacityMin": 1, "capacityMax": 6, "name": "1-6人"},
      {"capacityMin": 7, "capacityMax": 14, "name": "7-14人"},
      {"capacityMin": 15, "capacityMax": 21, "name": "15-21人"}
    ],
    "window": [
      {"id": 1, "name": "有窗"},
      {"id": 0, "name": "无窗"}
    ]
  }
}
```

#### 💡 使用缓存优化

条件列表数据基本固定，强烈建议使用缓存：

```python
from cache_manager import CacheManager

cache_manager = CacheManager()

# 1. 优先从缓存读取
conditions = cache_manager.get_conditions_cache()

# 2. 如果缓存无效，则从API获取
if not conditions:
    response = requests.get('https://calendar.sankuai.com/room/front/pc/room/moreInfo', headers=headers)
    result = response.json()
    conditions = result.get('data')
    
    # 保存到缓存
    cache_manager.save_conditions_cache(conditions)

# 3. 使用条件数据
capacity_list = conditions.get('capacity', [])
```

**根据用户人数选择容量范围**：
```python
def select_capacity(person_count, capacity_list):
    """根据人数选择合适的容量范围"""
    for cap in capacity_list:
        if cap['capacityMin'] <= person_count <= cap['capacityMax']:
            return cap
    return None

# 示例：7人会议
selected = select_capacity(7, capacity_list)
# 返回：{"capacityMin": 7, "capacityMax": 14, "name": "7-14人"}
```

### 步骤 3：筛选可用会议室

调用接口：`POST https://calendar.sankuai.com/meeting/api/pc/room/appointment/v2/find-rooms`

**请求体参数**：
```json
{
  "date": 1772553600000,
  "buildingId": "843",
  "floorIds": [],
  "capacity": [{"capacityMin": 7, "capacityMax": 14, "name": "7-14人"}],
  "startTime": "10:00",
  "endTime": "18:00"
}
```

| 参数 | 说明 |
|------|------|
| `date` | 查询日期的时间戳（毫秒，必须在 7 天内） |
| `buildingId` | 大楼 ID（字符串） |
| `floorIds` | 楼层 ID 数组，空数组表示不限楼层 |
| `capacity` | 容量范围对象数组 |
| `startTime/endTime` | 时间范围（HH:MM 格式） |

**返回数据包含**：会议室 ID、名称、容量、楼层、设备、邮箱、地址等信息。

#### ⚠️ 重要：验证查询结果

查询到会议室后，**必须验证返回的建筑信息是否正确**：

```python
# 查询会议室后的验证步骤
rooms = result.get('data', [])

for room in rooms:
    # 验证建筑名称是否与用户需求匹配
    print(f"会议室: {room['name']}")
    print(f"建筑: {room['buildingName']}")  # ← 必须检查这个字段
    print(f"楼层: {room['floorName']}")
    
    # 如果 buildingName 不包含用户要求的城市或建筑，说明 buildingId 错误
    if '上海' not in room['buildingName']:
        print("❌ 错误：查询到的不是上海的建筑，需要重新选择正确的 buildingId")
```

**验证清单**：
- ✅ 城市是否正确？（如：要求上海，结果是绍兴 → 错误）
- ✅ 建筑名称是否匹配？（如：要求D2栋，结果是环宇总部 → 错误）
- ✅ 楼层是否符合要求？（如果用户指定了楼层）

**如果验证失败**：
1. 返回到步骤1，重新获取建筑列表
2. 严格按照"城市 → 建筑"的层级查找
3. 使用正确的 buildingId 重新查询

### 步骤 4：查询会议室预订情况

调用接口：`POST https://calendar.sankuai.com/meeting/api/pc/room/appointment/findRoomAppointmentsV2`

**请求体参数**：
```json
{
  "date": 1772553600000,
  "roomIds": [11525, 11516, 11591]
}
```

**返回数据示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "roomId": 11516,
      "appointmentVOS": [
        {
          "id": "54986818",
          "title": "郝妍的会议",
          "startTime": 1772593200000,
          "endTime": 1772596800000,
          "isRecur": false
        }
      ]
    }
  ]
}
```

**分析返回结果**，找出用户指定时间段内没有预订记录的会议室。

### ⚠️ 重要：通过预订记录提前识别下线会议室

下线的会议室在预订记录接口中有一个明显特征：它会有一条 **时长超过 20 小时** 的预订记录（通常是全天占位）。在分析预订情况时，**必须先过滤掉这些下线会议室**，避免后续发起无效的预订请求。

```python
OFFLINE_THRESHOLD_MS = 20 * 60 * 60 * 1000  # 20小时，单位毫秒

free_rooms = []
offline_rooms = []
busy_rooms = []

for room in rooms_data:
    room_id = room['roomId']
    appointments = room.get('appointmentVOS', []) or []
    
    # 第一步：检查是否为下线会议室
    is_offline = False
    for appt in appointments:
        duration = appt['endTime'] - appt['startTime']
        if duration > OFFLINE_THRESHOLD_MS:
            is_offline = True
            break
    
    if is_offline:
        offline_rooms.append(room_id)
        continue  # 跳过下线会议室，不再判断时段冲突
    
    # 第二步：正常判断时段冲突
    has_conflict = any(
        appt['startTime'] < target_end and appt['endTime'] > target_start
        for appt in appointments
    )
    
    if has_conflict:
        busy_rooms.append(room_id)
    else:
        free_rooms.append(room_id)

print(f'空闲: {len(free_rooms)}, 已预订: {len(busy_rooms)}, 已下线: {len(offline_rooms)}')
```

**判断规则**：如果某条预订记录的 `endTime - startTime > 20小时`（72000000毫秒），则该会议室已下线，直接排除，不再尝试预订。

## 会议室预订提交

找到空闲会议室后，直接提交预订，**无需等待用户额外确认**。

### ⚠️ 重要：会议室下线处理（两层防护）

下线会议室的识别采用**两层防护**机制：

**第一层（预订记录预判）**：在查询预订情况时，通过预订时长 > 20小时的特征提前过滤掉下线会议室（见上方步骤4），避免发起无效请求。

**第二层（预订响应兜底）**：即使通过了第一层过滤，提交预订时仍可能遇到下线错误（如会议室刚刚下线、预订记录尚未更新等边缘情况），此时需要自动重试下一个：

```python
# 遍历空闲会议室（已排除预判为下线的），逐个尝试预订
for selected in free_rooms:
    resp = requests.post(book_url, headers=HEADERS, json=build_booking_body(selected))
    result = resp.json()
    
    if result.get('message') == '成功':
        print(f'✅ 预订成功: {selected["name"]}')
        break
    
    err_msg = result.get('data', {}).get('message', '')
    if '已下线' in err_msg:
        print(f'⚠️ {selected["name"]} 已下线，尝试下一个...')
        continue  # 跳过下线的会议室，尝试下一个
    else:
        print(f'❌ 预订失败: {err_msg}')
        break  # 其他错误直接停止
else:
    # 所有空闲会议室都下线或预订失败
    print('所有空闲会议室均不可用，自动创建空闲监测任务...')
    add_room_monitor(...)  # 触发监测
```

**下线会议室的错误响应**：
```json
{
  "data": {
    "message": "会议室已下线! 当前不支持预订及抢订!"
  },
  "rescode": 1
}
```

**关键规则**：
- **优先通过预订记录预判**：预订时长 > 20小时 → 直接标记为下线，不发起预订请求
- 遇到「会议室已下线」错误时，**不要停止**，继续尝试下一个空闲会议室
- 只有当所有空闲会议室都尝试失败后，才触发空闲监测
- 下线的会议室仍会出现在查询结果中，这是 API 的已知行为

### 提交接口

调用接口：`POST https://calendar.sankuai.com/api/v2/xm/schedules`

**请求体（完整参数格式）**：
```json
{
  "title": "会议主题",
  "startTime": 1772848800000,
  "endTime": 1772852400000,
  "isAllDay": 0,
  "location": "",
  "attendees": ["6485487"],
  "noticeType": 0,
  "noticeRule": "P0Y0M0DT0H10M0S",
  "recurrencePattern": {
    "type": "NONE",
    "showType": "NONE"
  },
  "deadline": 0,
  "memo": "",
  "organizer": "6485487",
  "room": {
    "id": 11486,
    "name": "富春厅",
    "email": "room-blx-2f-a-fuchunting@meituan.com",
    "capacity": 13,
    "floorId": 2001,
    "floorName": "2层",
    "buildingId": 843,
    "buildingName": "北京/保利广场西座"
  },
  "appKey": "meeting",
  "bookType": 11
}
```

**必填字段说明**：

| 字段 | 类型 | 说明 | 必填 |
|------|------|------|------|
| title | string | 会议标题 | 是 |
| startTime | number | 开始时间（毫秒时间戳） | 是 |
| endTime | number | 结束时间（毫秒时间戳） | 是 |
| isAllDay | number | 是否全天（0=否） | 是 |
| organizer | string | 组织者 ID（用户 MIS 账号对应的数字 ID，见下方"获取 organizer ID"） | 是 |
| attendees | array | 参与人员 ID 列表 | 是 |
| room | object | 会议室信息（需包含 id, name, email, capacity, floorId, floorName, buildingId, buildingName） | 是 |
| appKey | string | 应用标识（固定为"meeting"） | 是 |
| bookType | number | 预订类型（固定为11） | 是 |
| noticeType | number | 通知类型（固定为0） | 否 |
| recurrencePattern | object | 循环模式（固定为 {type:"NONE",showType:"NONE"}） | 否 |
| deadline | number | 截止时间（固定为0） | 否 |
| memo | string | 备忘录（留空） | 否 |
| location | string | 位置描述（留空） | 否 |

### 📋 获取 organizer ID

**organizer** 字段需要填写用户的员工 ID（empId），而不是 MIS 账号。可以通过以下接口查询：

**接口：查询员工信息**

```bash
curl 'https://calendar.sankuai.com/api/v2/xm/meeting/dataset/account' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'M-UserContext: eyJsb2NhbGUiOiJ6aCIsInRpbWVab25lIjoiQXNpYS9TaGFuZ2hhaSJ9' \
  -H 'Cookie: [你的Cookie]' \
  --data-raw '{"filter":"[员工MIS账号]"}'
```

**请求参数**：
- `filter`: 员工的 MIS 账号（如：`wb_yuanfangsheng`）

**返回示例**：
```json
{
  "data": [
    {
      "name": "袁芳胜",
      "empId": "22244841",
      "mis": "wb_yuanfangsheng",
      "email": "...",
      "avatar": "..."
    }
  ],
  "code": 200,
  "message": "success"
}
```

**提取 `empId`** 并用于 `organizer` 字段。

**自动化说明**：
- 当你提供 Cookie 后，我会自动调用此接口查询你的 empId
- 后续预订时自动使用该 ID，无需手动查询

### ⚠️ **时间戳计算方法**

使用精确的 Unix 毫秒时间戳（注意不能使用错误的计算方式）：

```python
from datetime import datetime, timezone, timedelta

# 正确方式：使用 timezone 对象
dt = datetime(2026, 3, 7, 10, 0, 0, tzinfo=timezone(timedelta(hours=8)))
timestamp_ms = int(dt.timestamp() * 1000)
```

### 提交后处理

**成功标志**：
- API 返回 `"message":"成功"`
- 或返回 `redirectUrl` 字段
- HTTP 状态码 200

**成功反馈**（包含以下信息）：
- ✅ 会议室名称
- ✅ 日期和时间段
- ✅ 地点（城市/大楼/楼层）
- ✅ 容量

**失败处理**：

| 失败原因 | 错误信息 | 处理建议 |
|----------|----------|----------|
| 时间参数格式错误 | "时间参数不合法" | 检查时间戳是否正确（使用毫秒级时间戳） |
| 预订过去时间 | "过去时间不可预订会议室" | 提示用户选择未来时间 |
| 会议室已被预订 | "会议室已被预订，请重新选择" | 选择其他会议室或改时间 |
| 查询超过7天 | "仅支持历史7天内的数据查询" | 提示用户只能预订7天内的会议室 |
| 登录失效 | "未登录" | 提示用户重新登录并更新 Cookie |
| 权限不匹配 | "权限不匹配，拒绝操作" | 检查 organizer 和 attendees 是否有效 |
| **没有空闲会议室** | **自动启动监测任务** | ✅ 系统自动调用空闲监测接口，为用户创建监测预约 |
| 会议室已下线 | "会议室已下线! 当前不支持预订及抢订!" | 优先通过预订时长>20h预判过滤；兜底：跳过该会议室，尝试下一个；全部不可用则触发监测 |
| 同时段预订数量超限 | "所选时段内已同时预订了2间会议室，请选择其他时间段预订吧~" | 提示用户该时段已预订2间会议室，建议取消一个或换时间 |

### 空闲会议室监测功能（自动化新增功能）

当系统在指定时间段内 **查不到任何空闲会议室** 时，会 **自动为用户创建空闲监测预约任务**，无需用户任何操作。

#### 📋 监测功能说明

**自动触发条件**（满足任一即触发）：
- 查询到的所有会议室都已被预订，没有空闲会议室
- 有空闲会议室但全部已下线，无法预订
- 空闲会议室因其他原因（如同时段限制）全部预订失败

**监测任务包含的信息**：
- 🏢 **建筑**：用户指定的建筑ID
- 🛢️ **楼层**：自动包含该建筑的所有楼层（或用户指定的楼层）
- 🕐 **时间范围**：用户指定的开始和结束时间戳（毫秒）
- 👥 **人数**：用户指定的容量需求

**监测返回示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": "添加成功，在 03-05 13:30 (GMT+08:00) 前会为你持续监测。"
}
```

**监测工作原理**：
1. ✅ 系统后台持续扫描该建筑的会议室状态
2. ✅ 在监测期限内（通常24小时内），如果有符合条件的空闲会议室出现
3. ✅ 系统会自动向你发送通知，告知可预订的会议室信息
4. ✅ 你收到通知后可直接预订，无需二次操作

**监测接口调用详情**：
```
POST https://calendar.sankuai.com/room/front/appointment-room/insertV2

请求体示例:
{
  "buildingId": 843,
  "planStartTimestamp": 1772688600000,
  "planEndTimestamp": 1772692200000,
  "floorIds": [2003, 2004],
  "headCount": 5
}

响应示例（成功）:
{
  "code": 200,
  "message": "success",
  "data": "添加成功，在 03-05 13:30 (GMT+08:00) 前会为你持续监测。"
}

响应示例（重复监测）:
{
  "code": 50801,
  "message": "该大厦下 14:00-16:00 (GMT+08:00) 已有监测，不可重复预约",
  "data": null
}
```

**⚠️ 监测接口需要额外请求头**（与普通预订接口不同）：
```python
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/plain, */*',
    'X-Requested-With': 'XMLHttpRequest',
    'M-UserContext': 'eyJsb2NhbGUiOiJ6aCIsInRpbWVab25lIjoiQXNpYS9TaGFuZ2hhaSJ9',
    'Referer': 'https://calendar.sankuai.com/rooms',   # ← 必须
    'tz': 'Asia/Shanghai',                              # ← 必须
    'la': 'zh',                                         # ← 必须
    'sec-ch-ua-platform': 'macOS',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 ...',
    'Cookie': cookie_string   # ← 必须使用 cookie.json 中的 cookie
}
```

**监测接口错误码说明**：

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 200 | 创建成功 | 提示用户监测已开启 |
| 50801 | 该时段已有监测任务 | 告知用户监测已存在，无需重复创建（这不是失败） |
| 401 | Cookie 认证失败 | 重新运行 login.py 获取新 Cookie |

**用户提示文案**：
```
❌ 03-05 19:00-20:00 没有空闲会议室
预订情况: 12 个房间已被预订

✅ 正在为您自动添加空闲监测...
✅ 已为您添加监测任务
   添加成功，在 03-05 13:30 (GMT+08:00) 前会为你持续监测。
```

## 常见问题处理

### Q: 用户说"明天上午"，如何处理？
**A**: 将"明天"转换为具体日期，"上午"默认为 10:00-11:00，询问用户确认。

### Q: 用户要求"4小时会议"但超出时长限制？
**A**: 提示单次最多 4 小时，建议分成两次预订或调整时长。

### Q: 没有找到空闲会议室，或空闲会议室全部已下线？
**A**: 系统会自动为你创建 **空闲监测预约**，无需手动操作。
- ✅ 自动调用监测接口（需要额外请求头，见监测接口说明）
- ✅ 在指定的城市、建筑、楼层和时间范围内持续监测空闲会议室
- ✅ 当有符合条件的空闲会议室时，系统会自动发送通知
- ✅ 如果返回错误码 50801，说明监测已存在，无需重复创建（这不是失败）
- 📋 你也可以手动返回所有候选会议室及其被占用时段，自行调整时间或选择其他地点

### Q: 用户只想查询可用性，不想预订？
**A**: 禁止提交，仅输出可用会议室列表。

### Q: 如何配置 Cookie？
**A**: 

**自动方式（推荐）** ⭐
运行 `login.py` 脚本自动获取并保存 Cookie 到 `cookie.json`：
```bash
cd ~/.catpaw/skills/room-booking-helper
python3 login.py
```
脚本会自动验证已有 Cookie 是否有效，过期则弹出浏览器引导 SSO 登录。

**手动方式**（如果 login.py 无法使用）：
1. 打开 https://calendar.sankuai.com 并完成 SSO 登录
2. 按 **F12** 打开开发者工具，在 Network 标签中复制任意请求的 Cookie 头
3. 编辑 `~/.catpaw/skills/room-booking-helper/cookie.json`，填入 cookie 字段

⚠️ **注意**：不要使用 `~/.catpaw/sso_config.json` 中的 ssoid，部分接口（如监测接口）不认识它。

### Q: 整个预订过程需要用户手动做什么吗？
**A**: 
完全不需要！只需告诉我预订需求，比如：
- "帮我订一个北京保利广场西座明天上午10点2小时的会议室，5个人"
- "查一下上海互联D2栋下午14-15点有没有空会议室"

**我会自动**：
✅ 调用所有 API 查询
✅ 执行 curl 命令
✅ 分析会议室信息
✅ 提交预订请求
✅ 返回预订结果

### Q: 可以保存 Cookie 以便下次使用吗？
**A**: 
可以！告诉我你的 Cookie 一次，我会记住它，后续所有操作都自动使用。
- 更新 Cookie：只需告诉我新的 Cookie 值
- 切换用户：告诉我新用户的 Cookie 即可

### Q: 如何获取 organizer ID（员工 ID）？
**A**: 

**自动方式（推荐）**：
告诉我你的 MIS 账号（如：`wb_yuanfangsheng`），我会：
- 自动调用员工信息查询接口
- 提取你的 empId
- 后续预订时自动使用

**手动方式**：
执行以下 curl 命令：
```bash
curl 'https://calendar.sankuai.com/api/v2/xm/meeting/dataset/account' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: [你的Cookie]' \
  --data-raw '{"filter":"[你的MIS账号]"}'
```

返回结果中的 `empId` 字段就是 organizer ID。

**示例**：
- 输入 MIS 账号：`wb_yuanfangsheng`
- 返回 empId：`22244841` ← 这个就是 organizer ID

### Q: organizer 和 attendees 的区别？
**A**: 
- **organizer**：会议组织者（发起人），必须是你自己的 empId
- **attendees**：参会人员列表（可包括多个人），数组格式，通常至少包含组织者本人

例如：
```json
{
  "organizer": "22244841",
  "attendees": ["22244841"]
}
```

## 关键提示

### 🔐 Cookie 和请求头注意事项（重要！）

**经验教训**：Cookie 中可能包含 `**` 等特殊字符，这是编码的一部分，**不需要转义**。

**正确做法**：
1. 从 `~/.catpaw/skills/room-booking-helper/cookie.json` 读取 `cookie` 字段（不是 sso_config.json）
2. **不要尝试修改、转义或分割** Cookie 值
3. 在请求头中原样使用即可
4. 必须添加完整的请求头 (Content-Type、X-Requested-With、M-UserContext 等)

**错误做法** ❌：
```python
# 不要这样做！
cookie = config['ssoid'].replace('**', '%2A%2A')  # 错误：不需要转义
# 也不要从 sso_config.json 读取 ssoid，监测接口不认识
```

**正确做法** ✅：
```python
import json, os

# 始终从 cookie.json 读取
COOKIE_PATH = os.path.expanduser('~/.catpaw/skills/room-booking-helper/cookie.json')
with open(COOKIE_PATH) as f:
    cred = json.load(f)

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/plain, */*',
    'X-Requested-With': 'XMLHttpRequest',
    'M-UserContext': 'eyJsb2NhbGUiOiJ6aCIsInRpbWVab25lIjoiQXNpYS9TaGFuZ2hhaSJ9',
    'User-Agent': 'Mozilla/5.0 ...',
    'Cookie': cred['cookie']  # 直接使用 cookie.json 中的 cookie 字段
}
response = requests.post(url, headers=headers)
```

### 🤖 自动化能力
- **API 调用自动化**：使用 requests 或 curl 命令自动调用所有接口，无需手动操作
- **参数处理自动化**：自动计算时间戳、构建请求体、解析响应
- **流程自动化**：从查询到预订的全流程一键执行
- **结果展示自动化**：自动格式化输出，提供清晰的预订确认信息

### ⚙️ 技术细节
- **Cookie 管理**：支持自动获取和保存，避免手动输入。Cookie 中包含特殊字符属于正常编码
- **时间戳转换**：自动转换为毫秒级 Unix 时间戳（北京时间 UTC+8）
- **查询限制**：自动检查 7 天范围限制，提示用户调整
- **完整参数**：自动补全所有必填参数，确保请求成功
- **HTTP 方法**：注意区分 GET 和 POST 方法，不同接口要求不同

### 📱 用户体验
- **零手动操作**：只需提供自然语言预订需求
- **智能纠正**：对无效输入自动提示和纠正
- **失败重试**：遇到临时失败自动重试或建议替代方案
- **进度反馈**：实时显示各步骤进度

## 执行流程（核心，必须严格遵循）

基于大量实际预订经验优化的最快执行流程。**关键原则：最少工具调用次数 = 最快预订速度。**

### 🚀 最快路径：一次性脚本（推荐！）

**只需 2 次工具调用即可完成全流程：**

1. **SSO 登录**（如果 cookie.json 不存在或过期）
2. **运行 quick_book.py**（一次性完成：定位建筑→查房间→查预订→批量预订→监测兜底）

```bash
# 一次性预订命令
python3 ~/.openclaw/skills/room-booking-helper\ 2/resources/quick_book.py \
  --city 上海 --building D2 --date 2026-03-10 --start 12:00 --end 13:00 \
  --capacity 5 --mis wangjun137
```

**参数说明**：
| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| --city | ✅ | 城市关键词 | 上海、北京、成都 |
| --building | ✅ | 建筑关键词 | D2、保利、互联 |
| --date | ✅ | 日期 YYYY-MM-DD | 2026-03-10 |
| --start | ✅ | 开始时间 HH:MM | 12:00 |
| --end | ✅ | 结束时间 HH:MM | 13:00 |
| --capacity | ❌ | 容量需求（默认5） | 10 |
| --mis | ❌ | MIS账号（默认从cookie.json读取） | wangjun137 |

**脚本自动处理**：
- ✅ 从缓存定位建筑（缓存不存在自动获取并保存）
- ✅ 查询会议室列表
- ✅ 查询预订情况，筛选空闲（检查时间重叠 + 过滤下线会议室）
- ✅ 批量尝试预订，遇到成功立即返回
- ✅ 全部失败时自动创建监测任务

**输出示例**：
```
✅ 建筑: 上海/互联D2栋 (ID:335)
✅ 候选: 35 个
✅ 空闲:17 占用:18 下线:0

==================================================
✅ 预订成功！
  room: 铜陵厅
  floor: 2层
  capacity: 5
  building: 上海/互联D2栋
  date: 2026-03-10
  time: 12:00-13:00
  schedule_id: 2031207149161762906
==================================================
```

### 完整流程（仅在 quick_book.py 不可用时使用）

#### 步骤 1：信息收集（0 次工具调用）
- ✅ 从自然语言中提取：城市、建筑、日期、时间、人数
- ✅ 校验预订时间合法性（7天内、未来时间）
- ✅ 自动填充缺失的默认值
- ✅ 根据人数确定容量范围：1-6人、7-14人、15-21人、22-40人、41-60人、61+人

#### 步骤 2：SSO 登录（1 次工具调用，如需要）

检查 `~/.openclaw/skills/room-booking-helper 2/cookie.json` 是否存在：
- 存在且有效 → 跳过
- 不存在或过期 → 执行 SSO 登录

```bash
bash "$HOME/.openclaw/skills/room-booking-helper 2/scripts/sso-login.sh" <misId>
```

用户需要在大象上确认授权，完成后 Cookie 会自动保存到 cookie.json。

#### 步骤 3：执行预订（1 次工具调用）

直接调用 quick_book.py：

```bash
python3 "$HOME/.openclaw/skills/room-booking-helper 2/resources/quick_book.py" \
  --city <城市> --building <建筑> --date <日期> --start <开始> --end <结束> \
  [--capacity <人数>] [--mis <MIS账号>]
```

#### 步骤 4：结果确认
- ✅ 展示预订成功的完整信息（会议室名、楼层、容量、时间、会议ID）
- ✅ 如触发监测，展示监测任务创建结果

### 工具调用次数对比

| 场景 | 旧方案 | 优化后 |
|------|--------|--------|
| 首次预订（需登录） | 5-10 次 | **2 次**（SSO + quick_book） |
| 后续预订（已登录） | 4-6 次 | **1 次**（quick_book） |

### 备用方案：Python 脚本分步执行

如果 quick_book.py 不可用，可以用 Python requests 分步执行：

```python
import json, requests
from datetime import datetime, timezone, timedelta

# 1. 读取 cookie
with open('~/.openclaw/skills/room-booking-helper 2/cookie.json') as f:
    cookie = json.load(f)['cookie']

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/plain, */*',
    'X-Requested-With': 'XMLHttpRequest',
    'M-UserContext': 'eyJsb2NhbGUiOiJ6aCIsInRpbWVab25lIjoiQXNpYS9TaGFuZ2hhaSJ9',
    'Cookie': cookie
}

# 2. 定位建筑（从缓存或 API）
# 3. 查询会议室
# 4. 查询预订情况
# 5. 筛选空闲 + 批量尝试预订
# （详见原文档的 API 调用说明）
```

| 查询预订情况 | 1次 | 0次（大多数场景跳过） |
| 提交预订 | 1-N次（逐个尝试） | 1次（批量 JS 循环） |
| **总计** | **5-10+次** | **2-3次** |

## 缓存优化常见问题

### Q: 缓存是如何工作的？
**A**: 

**建筑缓存（buildings_cache.json）**：
1. **第一次运行**：从 API 获取城市、建筑、楼层列表并保存
2. **后续运行**：检查缓存文件是否存在且有效（7 天内），如果有效直接使用
3. **自动过期**：超过 7 天自动判定为过期，下次使用时重新获取
4. **性能提升**：省去获取建筑列表的时间（约 1.5 秒）

**条件缓存（conditions_cache.json）**：
1. **第一次运行**：从 API 获取设备、容量、窗户等条件列表并保存
2. **后续运行**：直接从缓存读取（这些数据基本固定）
3. **性能提升**：省去获取条件列表的时间（约 0.5 秒）

**总体性能提升**：约 2 秒，预订速度提快约 40%

### Q: 缓存占用多少存储空间？
**A**: 
- **建筑缓存**：约 500KB（包含全国所有城市、建筑、楼层信息，使用新接口后数据量减少约 36%）
- **条件缓存**：约 1KB（设备、容量、窗户等条件）
- **总计**：约 501KB，非常小，不会影响系统存储

### Q: 如何清除缓存？
**A**: 
使用缓存管理工具清除：
```bash
# 清除所有缓存
python ~/.catpaw/skills/room-booking-helper/resources/manage_cache.py clear-all

# 或分别清除
python ~/.catpaw/skills/room-booking-helper/resources/manage_cache.py clear-buildings
python ~/.catpaw/skills/room-booking-helper/resources/manage_cache.py clear-conditions
```

### Q: 如何查看缓存状态？
**A**: 
```bash
python ~/.catpaw/skills/room-booking-helper/resources/manage_cache.py status
```
会显示：
- 缓存是否有效
- 缓存文件是否存在
- 缓存过期时间
- 缓存文件路径

### Q: 缓存数据会过期吗？
**A**: 
是的，缓存有 7 天的有效期。这样设计是为了：
- 确保数据新鲜度（新增建筑、楼层等会在 7 天内更新）
- 平衡性能和数据准确性
- 自动处理，无需手动干预

如需立即使用最新数据，可手动清除缓存。

### Q: 能否禁用缓存？
**A**: 
可以，有两种方式：
1. **临时禁用**：清除缓存后立即使用，缓存会重新建立
2. **永久禁用**：编辑 `resources/cache_manager.py`，修改 `CACHE_EXPIRY_DAYS = 0`

### Q: 缓存是否会导致数据不一致？
**A**: 
不会。缓存仅用于存储相对稳定的数据（城市、建筑、楼层），这些数据变化频率很低。
实时数据（会议室预订情况、时间等）每次都是从 API 获取，确保数据一致性。

### Q: 能否手动更新缓存？
**A**: 
支持。需要立即更新缓存时：
1. 清除旧缓存：`python resources/manage_cache.py clear-buildings`
2. 运行任意预订命令，会自动重新获取并缓存最新数据

### Q: 缓存在哪个目录？
**A**: 
```
~/.catpaw/skills/room-booking-helper/resources/cache/
├── buildings_cache.json      # 建筑数据缓存
└── conditions_cache.json     # 条件数据缓存（可选）
```

### Q: 如果缓存文件损坏怎么办？
**A**: 
直接删除损坏的缓存文件，系统会自动重新创建：
```bash
rm ~/.catpaw/skills/room-booking-helper/resources/cache/*.json
```

### Q: 缓存是否支持多用户？
**A**: 
不建议多用户共享同一个缓存目录。每个用户应该有自己的配置和缓存。
如需多用户支持，请在 `SKILL.md` 中反馈，我们可以改进为每用户独立缓存。

---

## 详细参考资源

- 完整的 API 参数详细说明，见 [reference.md](reference.md)
- 实际使用示例和对话案例，见 [examples.md](examples.md)
- 缓存优化详细文档，见 [resources/README.md](resources/README.md)
- 缓存管理命令，见 [resources/manage_cache.py](resources/manage_cache.py)
