# 会议室预订 API 详细参考

## API 端点列表

| 功能 | 端点 | 方法 |
|------|------|------|
| 获取城市/大厦/楼层 | `/meeting/api/pc/room/appointment/findCityBuildingAndFloor` | POST |
| 获取筛选条件 | `/room/front/pc/room/moreInfo` | POST |
| 查询可用会议室 | `/meeting/api/pc/room/appointment/v2/find-rooms` | POST |
| 查询会议室预订 | `/meeting/api/pc/room/appointment/findRoomAppointmentsV2` | POST |
| 提交预订 | `/api/v2/xm/schedules` | POST |
| **创建空闲监测任务** | **/room/front/appointment-room/insertV2** | **POST** |

基础 URL：`https://calendar.sankuai.com`

---

## API 1: 获取城市、大厦和楼层列表

**端点**: `POST /meeting/api/pc/room/appointment/findCityBuildingAndFloor`

**请求头**：
```
Accept: application/json, text/plain, */*
Content-Type: application/json
Content-Length: 0
M-UserContext: eyJsb2NhbGUiOiJ6aCIsInRpbWVab25lIjoiQXNpYS9TaGFuZ2hhaSJ9
```

**请求体**：无（或空 JSON `{}` ）

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "cityId": 3531,
      "cityName": "北京市",
      "cityPriority": 10,
      "buildingAndFloorVoList": [
        {
          "building": {
            "id": 843,
            "name": "北京/保利广场西座",
            "memo": null,
            "disabled": 0,
            "sort": 0,
            "cityId": 3531,
            "orgSiteCodeId": "S000100821"
          },
          "floors": [
            {
              "id": 2001,
              "name": "2层",
              "disabled": 0,
              "map": "https://s3plus.meituan.net/v1/.../保利2F平面图SVG.svg",
              "buildingId": 843,
              "buildingName": "北京/保利广场西座",
              "sort": 0,
              "mapStatus": 1,
              "numFloor": 2
            },
            {
              "id": 2002,
              "name": "3层",
              "disabled": 0,
              "map": "https://s3plus.meituan.net/v1/.../保利3F平面图SVG.svg",
              "buildingId": 843,
              "buildingName": "北京/保利广场西座",
              "sort": 0,
              "mapStatus": 1,
              "numFloor": 3
            }
          ]
        }
      ]
    }
  ]
}
```

**关键字段说明**：
- `cityId`: 城市唯一标识
- `building.id`: 大厦 ID（在 API 3 中使用）
- `floors[].id`: 楼层 ID（在 API 3 中使用）

---

## API 2: 获取筛选条件列表

**端点**: `POST /room/front/pc/room/moreInfo`

**请求参数**：无

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "equips": [
      {
        "id": 7,
        "name": "Zoom"
      },
      {
        "id": 9,
        "name": "腾讯会议"
      },
      {
        "id": 8,
        "name": "无线投屏"
      },
      {
        "id": 2,
        "name": "投影"
      },
      {
        "id": 3,
        "name": "电视"
      }
    ],
    "capacity": [
      {
        "capacityMin": 1,
        "capacityMax": 6,
        "name": "1-6人"
      },
      {
        "capacityMin": 7,
        "capacityMax": 14,
        "name": "7-14人"
      },
      {
        "capacityMin": 15,
        "capacityMax": 21,
        "name": "15-21人"
      },
      {
        "capacityMin": 22,
        "capacityMax": 40,
        "name": "22-40人"
      },
      {
        "capacityMin": 41,
        "capacityMax": 60,
        "name": "41-60人"
      },
      {
        "capacityMin": 61,
        "capacityMax": 1000,
        "name": "61人及以上"
      }
    ],
    "window": [
      {
        "code": "EXIST",
        "name": "有窗"
      }
    ]
  }
}
```

**容量匹配逻辑**：
- 1-6 人 → 选择 `capacityMin: 1, capacityMax: 6`
- 7-14 人 → 选择 `capacityMin: 7, capacityMax: 14`
- 15-21 人 → 选择 `capacityMin: 15, capacityMax: 21`
- 22-40 人 → 选择 `capacityMin: 22, capacityMax: 40`
- 41-60 人 → 选择 `capacityMin: 41, capacityMax: 60`
- 60+ 人 → 选择 `capacityMin: 61, capacityMax: 1000`

---

## API 3: 查询可用会议室

**端点**: `POST /meeting/api/pc/room/appointment/v2/find-rooms`

**请求头**：
```
Content-Type: application/json
```

**请求体**：
```json
{
  "date": 1772553600000,
  "buildingId": "843",
  "floorIds": [],
  "capacity": [
    {
      "capacityMin": 7,
      "capacityMax": 14,
      "name": "7-14人"
    }
  ],
  "startTime": "10:00",
  "endTime": "18:00"
}
```

**参数说明**：

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `date` | number | 是 | 日期零点的毫秒时间戳 | `1772553600000` |
| `buildingId` | string | 是 | 大厦 ID（从 API 1 获取） | `"843"` |
| `floorIds` | array | 否 | 楼层 ID 数组，空表示不限 | `[]` 或 `[2001, 2002]` |
| `capacity` | array | 否 | 容量范围对象数组 | 见 API 2 |
| `startTime` | string | 是 | 开始时间（24小时制） | `"10:00"` |
| `endTime` | string | 是 | 结束时间（24小时制） | `"18:00"` |

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 11516,
      "name": "濮阳厅",
      "email": "room-blx-2f-d-puyangting@meituan.com",
      "capacity": 13,
      "disabled": 0,
      "floorId": 2001,
      "floorName": "2层",
      "buildingId": 843,
      "buildingName": "北京/保利广场西座",
      "equips": [
        {
          "equipId": 7,
          "equipName": "Zoom"
        }
      ],
      "memo": "该会议室已上线Zoom占位检测无人后自动释放功能，请预订后及时前往会议室使用。",
      "bookCardMemo": "该会议室已上线Zoom占位检测无人后自动释放功能，请预订后及时前往会议室使用。",
      "roomName": "濮阳厅",
      "roomMap": "https://s3plus.meituan.net/.../濮阳厅_1764839462880.png",
      "price": null,
      "pointX": 0.641860465116279,
      "pointY": 0.19590490680870065,
      "window": "NOT_EXIST",
      "roomLocationUrl": "https://123.sankuai.com/huiyi/map/dx?id=11516"
    },
    {
      "id": 11608,
      "name": "淮河厅",
      "capacity": 5,
      "floorId": 2003,
      "floorName": "4层",
      "window": "EXIST"
    }
  ]
}
```

**关键字段说明**：
- `id`: 会议室 ID（在 API 4、API 5 中使用）
- `name`: 会议室名称
- `capacity`: 会议室容量
- `equips`: 会议室设备列表
- `memo`: 会议室备注说明
- `window`: 是否有窗户 (`EXIST` / `NOT_EXIST`)

---

## API 4: 查询会议室预订情况

**端点**: `POST /meeting/api/pc/room/appointment/findRoomAppointmentsV2`

**请求头**：
```
Content-Type: application/json
```

**请求体**：
```json
{
  "date": 1772553600000,
  "roomIds": [11525, 11516, 11591]
}
```

**参数说明**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `date` | number | 是 | 日期零点的毫秒时间戳 |
| `roomIds` | array | 是 | 会议室 ID 数组（从 API 3 获取） |

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "roomId": 11516,
      "appKey": "meeting",
      "entryList": null,
      "appointmentVOS": [
        {
          "id": "54986818",
          "scheduleId": "2028812952760832035",
          "title": "郝妍的会议",
          "isOrganizer": 0,
          "startTime": 1772593200000,
          "endTime": 1772596800000,
          "isRecur": false
        },
        {
          "id": "55222216",
          "scheduleId": "2029090334139371533",
          "title": "徐坤鹏的会议",
          "isOrganizer": 0,
          "startTime": 1772608500000,
          "endTime": 1772611200000,
          "isRecur": false
        }
      ]
    },
    {
      "roomId": 11591,
      "appointmentVOS": []
    }
  ]
}
```

**字段说明**：
- `roomId`: 会议室 ID
- `appointmentVOS[].title`: 预订的会议标题
- `appointmentVOS[].startTime`: 开始时间（毫秒时间戳）
- `appointmentVOS[].endTime`: 结束时间（毫秒时间戳）
- 空数组 `[]` 表示该会议室当天无预订

**空闲时段判断**：
1. 如果 `appointmentVOS` 为空数组，整天都空闲
2. **先检查是否为下线会议室**：如果任一预订记录的 `endTime - startTime > 20小时`（72000000ms），则该会议室已下线，直接排除，不再尝试预订
3. 遍历 `appointmentVOS` 检查用户指定的时间段是否与任何预订重叠
4. 无重叠 = 空闲

---

## API 5: 提交预订

**端点**: `POST /api/v2/xm/schedules`

**请求头**：
```
Content-Type: application/json
Cookie: [浏览器当前cookie]
```

**请求体（完整格式）**：
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
    "disabled": 0,
    "floorId": 2001,
    "floorName": "2层",
    "buildingId": 843,
    "buildingName": "北京/保利广场西座"
  },
  "appKey": "meeting",
  "bookType": 11
}
```

**参数说明**：

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `title` | string | 是 | 会议标题 | "周会" |
| `startTime` | number | 是 | 开始时间（毫秒时间戳） | `1772848800000` |
| `endTime` | number | 是 | 结束时间（毫秒时间戳） | `1772852400000` |
| `isAllDay` | number | 是 | 是否全天 | `0` (不全天) |
| `organizer` | string | 是 | 组织者 ID（数字 ID） | `"6485487"` |
| `attendees` | array | 是 | 参与人员 ID 列表 | `["6485487"]` |
| `room.id` | number | 是 | 会议室 ID | `11486` |
| `room.name` | string | 是 | 会议室名称 | `"富春厅"` |
| `room.email` | string | 是 | 会议室邮箱 | `"room-blx-2f-a-fuchunting@meituan.com"` |
| `room.capacity` | number | 是 | 会议室容量 | `13` |
| `room.floorId` | number | 是 | 楼层 ID | `2001` |
| `room.floorName` | string | 是 | 楼层名称 | `"2层"` |
| `room.buildingId` | number | 是 | 大厦 ID | `843` |
| `room.buildingName` | string | 是 | 大厦名称 | `"北京/保利广场西座"` |
| `appKey` | string | 是 | 应用标识 | `"meeting"` |
| `bookType` | number | 是 | 预订类型 | `11` |
| `noticeType` | number | 否 | 通知类型 | `0` |
| `recurrencePattern` | object | 否 | 循环模式 | `{"type":"NONE","showType":"NONE"}` |
| `deadline` | number | 否 | 截止时间 | `0` |
| `memo` | string | 否 | 备忘录 | `""` |
| `location` | string | 否 | 位置描述 | `""` |

**成功响应**：
```json
{
  "code": 200,
  "message": "成功",
  "redirectUrl": "/schedules/2028812952760832035",
  "data": null
}
```

**常见失败响应**：

1. **时间参数不合法**：
```json
{
  "data": {
    "message": "时间参数不合法"
  },
  "rescode": 1
}
```

2. **过去时间不可预订**：
```json
{
  "data": {
    "message": "过去时间不可预订会议室"
  },
  "rescode": 1
}
```

3. **会议室已被预订**：
```json
{
  "data": {
    "message": "会议室已被预订，请重新选择！"
  },
  "rescode": 1
}
```

4. **权限不匹配**：
```json
{
  "data": {
    "errorCode": "PERMISSION_REJECT",
    "message": "权限不匹配，拒绝操作"
  },
  "rescode": 1
}
```

5. **未登录**：
```json
{
  "data": {
    "message": "未登录"
  },
  "rescode": 1
}
```

---

## 时间戳转换

### JavaScript 示例：
```javascript
// 获取日期的零点时间戳（毫秒）
function getDateTimeStamp(dateStr) {
  return new Date(dateStr + ' 00:00:00').getTime();
}

// 获取具体时间的时间戳
function getTimeStamp(dateStr, timeStr) {
  return new Date(dateStr + ' ' + timeStr).getTime();
}
```

### 常用日期时间戳：
- 2026-02-18 00:00:00 → `1772553600000`
- 2026-02-18 10:00:00 → `1772619300000`
- 2026-02-18 11:00:00 → `1772622900000`

---

## Cookie 管理

所有 API 调用必须在 HTTP 请求头中携带有效的 Cookie。

**获取 Cookie**：
1. 在浏览器中打开 https://calendar.sankuai.com
2. 完成 SSO 登录
3. 打开浏览器开发者工具（F12）
4. 在 Application → Cookies 中查看当前 domain 的 Cookie
5. 复制整个 Cookie 字符串

**Cookie 示例**：
```
com.sankuai.xzfe.meeting.roomsweb_strategy=; 37facae47f_ssoid=eAGF...; sso_user_mis=wangjun137; plus_token=rOq-...; phmac=Tc2j...
```

---

## API 6: 创建空闲会议室监测任务（新增）

**端点**: `POST /room/front/appointment-room/insertV2`

**功能**：当没有找到符合条件的空闲会议室时，为用户自动创建监测预约任务。系统会在指定的时间段内持续监测该建筑的会议室状态，如果有符合条件的空闲会议室出现，会自动向用户发送通知。

**请求头**：
```
Accept: application/json, text/plain, */*
Content-Type: application/json
X-Requested-With: XMLHttpRequest
M-UserContext: eyJsb2NhbGUiOiJ6aCIsInRpbWVab25lIjoiQXNpYS9TaGFuZ2hhaSJ9
Referer: https://calendar.sankuai.com/rooms
tz: Asia/Shanghai
la: zh
sec-ch-ua-platform: macOS
sec-ch-ua: "Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"
sec-ch-ua-mobile: ?0
Cookie: [用户的Cookie]
```

**请求体参数**：
```json
{
  "buildingId": 843,
  "planStartTimestamp": 1772688600000,
  "planEndTimestamp": 1772692200000,
  "floorIds": [2003, 2004],
  "headCount": 5
}
```

| 参数 | 类型 | 说明 | 必填 |
|------|------|------|------|
| `buildingId` | number | 建筑ID | 是 |
| `planStartTimestamp` | number | 开始时间的毫秒时间戳 | 是 |
| `planEndTimestamp` | number | 结束时间的毫秒时间戳 | 是 |
| `floorIds` | array | 楼层ID列表（支持空数组表示不限楼层） | 否 |
| `headCount` | number | 人数需求 | 是 |

**成功响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": "添加成功，在 03-05 13:30 (GMT+08:00) 前会为你持续监测。"
}
```

**失败响应示例**：
```json
{
  "code": 400,
  "message": "参数错误",
  "data": null
}
```

**响应说明**：
- `code: 200`：监测任务创建成功
- `data` 字段包含监测的过期时间说明
- 用户会在监测期限前收到通知（如果有符合条件的空闲会议室）

**使用场景**：
1. 用户查询会议室时，发现指定时间段所有房间都已被预订
2. 系统自动调用此接口，为用户创建监测任务
3. 用户无需任何额外操作，系统后台持续监测
4. 有空闲会议室出现时，系统自动通知用户

**Python 调用示例**：
```python
import json
import urllib.request

headers = {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    'M-UserContext': 'eyJsb2NhbGUiOiJ6aCIsInRpbWVab25lIjoiQXNpYS9TaGFuZ2hhaSJ9',
    'Cookie': 'your_cookie_here'
}

data = {
    "buildingId": 843,
    "planStartTimestamp": 1772688600000,
    "planEndTimestamp": 1772692200000,
    "floorIds": [2003, 2004],
    "headCount": 5
}

req = urllib.request.Request(
    'https://calendar.sankuai.com/room/front/appointment-room/insertV2',
    data=json.dumps(data).encode('utf-8'),
    headers=headers,
    method='POST'
)

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode('utf-8'))
    print(result)
```

---

## 错误排查

| 错误信息 | 可能原因 | 解决方案 |
|----------|---------|---------|
| `code: 401` | Cookie 过期或未登录 | 重新登录获取新 Cookie |
| `code: 4001` | 该时间段已被预订 | 选择其他时间或会议室 |
| `code: 403` | 权限不足 | 检查账户权限或联系管理员 |
| `code: 500` | 服务器错误 | 稍后重试 |
| `code: 10001` | 请求参数错误 | 检查参数格式和时间戳 |
| 监测创建失败 | buildingId 或时间戳格式错误 | 验证参数是否正确（使用毫秒级时间戳） |
