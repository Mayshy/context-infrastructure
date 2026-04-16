#!/usr/bin/env python3
"""
缓存管理工具

用法:
  python manage_cache.py status    - 查看缓存状态
  python manage_cache.py clear-buildings   - 清除建筑缓存
  python manage_cache.py clear-conditions  - 清除条件缓存
  python manage_cache.py clear-all         - 清除所有缓存
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cache_manager import CacheManager

def print_status():
    """打印缓存状态"""
    cache = CacheManager()
    status = cache.get_cache_status()
    
    print("\n" + "="*60)
    print("缓存管理状态")
    print("="*60 + "\n")
    
    print(f"建筑缓存:")
    print(f"  ✅ 有效: {status['buildings']['valid']}")
    print(f"  📂 存在: {status['buildings']['exists']}")
    print(f"  📍 路径: {status['buildings']['path']}")
    
    print(f"\n条件缓存:")
    print(f"  ✅ 有效: {status['conditions']['valid']}")
    print(f"  📂 存在: {status['conditions']['exists']}")
    print(f"  📍 路径: {status['conditions']['path']}")
    
    print(f"\n缓存过期时间: {status['expiry_days']} 天")
    print("\n" + "="*60 + "\n")

def clear_buildings():
    """清除建筑缓存"""
    cache = CacheManager()
    if cache.clear_buildings_cache():
        print("✅ 建筑缓存已清除")
    else:
        print("❌ 清除建筑缓存失败")

def clear_conditions():
    """清除条件缓存"""
    cache = CacheManager()
    if cache.clear_conditions_cache():
        print("✅ 条件缓存已清除")
    else:
        print("❌ 清除条件缓存失败")

def clear_all():
    """清除所有缓存"""
    cache = CacheManager()
    if cache.clear_all_cache():
        print("✅ 所有缓存已清除")
    else:
        print("❌ 清除缓存失败")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("缓存管理工具")
        print("用法:")
        print("  python manage_cache.py status          - 查看缓存状态")
        print("  python manage_cache.py clear-buildings - 清除建筑缓存")
        print("  python manage_cache.py clear-conditions- 清除条件缓存")
        print("  python manage_cache.py clear-all       - 清除所有缓存")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == 'status':
        print_status()
    elif command == 'clear-buildings':
        clear_buildings()
    elif command == 'clear-conditions':
        clear_conditions()
    elif command == 'clear-all':
        clear_all()
    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)
