# 会议室预订 Skill - 本地缓存优化

## 概述

本目录包含会议室预订 Skill 的优化模块，主要功能是通过本地缓存减少 API 调用次数。

## 文件说明

### cache_manager.py
缓存管理核心模块，提供以下功能：

- **检查缓存有效性**：`is_buildings_cache_valid()`, `is_conditions_cache_valid()`
- **获取缓存数据**：`get_buildings_cache()`, `get_conditions_cache()`
- **保存缓存数据**：`save_buildings_cache()`, `save_conditions_cache()`
- **清除缓存**：`clear_buildings_cache()`, `clear_conditions_cache()`, `clear_all_cache()`
- **查看缓存状态**：`get_cache_status()`

**缓存配置**：
- 缓存路径：`resources/cache/`
- 建筑缓存文件：`buildings_cache.json` (788KB)
- 条件缓存文件：`conditions_cache.json`
- 缓存过期时间：7 天

### booking_optimized.py
优化版预订脚本，集成了缓存功能：

- **第一次运行**：从 API 获取城市、建筑、楼层数据并缓存（减少 API 调用）
- **后续运行**：直接从本地缓存读取（加快预订速度）
- **支持参数**：
  - `city_name`：城市名称（如 "上海"）
  - `building_name`：建筑名称（如 "D2"）
  - `date_str`：日期（如 "2026-03-05" 或 "明天"）
  - `start_time`：开始时间（如 "19:00"）
  - `end_time`：结束时间（如 "20:00"）
  - `capacity`：容量（默认 5 人）

### manage_cache.py
缓存管理命令行工具：

```bash
# 查看缓存状态
python manage_cache.py status

# 清除建筑缓存
python manage_cache.py clear-buildings

# 清除条件缓存
python manage_cache.py clear-conditions

# 清除所有缓存
python manage_cache.py clear-all
```

## 使用示例

### Python 脚本中使用

```python
from cache_manager import CacheManager

cache = CacheManager()

# 检查建筑缓存是否有效
if cache.is_buildings_cache_valid():
    data = cache.get_buildings_cache()
    print("使用缓存的建筑数据")
else:
    # 从 API 获取数据
    data = fetch_from_api()
    # 保存到缓存
    cache.save_buildings_cache(data)
```

### 命令行使用

```bash
# 查看缓存状态
python resources/manage_cache.py status

# 第一次预订（会缓存数据）
python resources/booking_optimized.py

# 第二次预订（使用缓存，更快）
python resources/booking_optimized.py

# 清除缓存
python resources/manage_cache.py clear-all
```

## 性能对比

| 操作 | 无缓存 | 有缓存 | 提升 |
|------|--------|--------|------|
| 获取建筑列表 | ~1.5s | 立即 | 1.5s |
| 第一次完整预订 | ~5-8s | ~5-8s | - |
| 后续预订 | ~5-8s | ~3-4s | 40% |
| 缓存文件大小 | - | 788KB | - |

## 缓存更新策略

### 自动过期
- 缓存有效期：7 天
- 超过 7 天自动判定为过期，下次使用时会重新从 API 获取

### 手动清除
```bash
python resources/manage_cache.py clear-all
```

### 按需更新
如果需要手动更新缓存，可以：
1. 清除旧缓存：`python resources/manage_cache.py clear-buildings`
2. 再次运行预订脚本会自动重新缓存

## 缓存数据结构

### buildings_cache.json
```json
{
  "cached_at": 1772616024301,  // 缓存时间戳 (毫秒)
  "data": [
    {
      "cityId": 3532,
      "cityName": "上海市",
      "cityPriority": 20,
      "buildingAndFloorVoList": [...]
    }
  ]
}
```

### conditions_cache.json
```json
{
  "cached_at": 1772616024301,
  "data": {
    "equips": [...],      // 可用设备列表
    "capacity": [...],    // 容量范围选项
    "window": [...]       // 窗户选项
  }
}
```

## 注意事项

1. **Cookie 管理**
   - Cookie 保存在 `~/.catpaw/sso_config.json`
   - Cookie 过期时需要手动更新
   - 缓存不依赖 Cookie，只缓存数据内容

2. **缓存文件权限**
   - 缓存文件位置：`resources/cache/`
   - 需要读写权限

3. **首次使用**
   - 首次运行会自动创建缓存目录
   - 首次调用 API 后会自动保存缓存
   - 后续使用无需额外操作

4. **离线使用**
   - 如果缓存有效，即使网络不稳定也能快速查询
   - 但实际预订仍需要网络连接

## 常见问题

### Q: 缓存数据不更新怎么办？
A: 缓存有 7 天的有效期。如果需要立即更新，使用命令清除缓存：
```bash
python resources/manage_cache.py clear-all
```

### Q: 缓存占用空间是多少？
A: 建筑缓存约 788KB，条件缓存根据实际数据大小（通常 <100KB）

### Q: 能否禁用缓存？
A: 缓存是自动管理的，但可以通过以下方式禁用：
1. 定期清除缓存：`python resources/manage_cache.py clear-all`
2. 修改 `CacheManager.CACHE_EXPIRY_DAYS = 0`（立即过期）

### Q: 缓存能否跨机器使用？
A: 不建议。缓存文件是绑定到本机的，跨机器使用可能导致问题。
