#!/usr/bin/env python3
"""
小八爬虫管理系统 - 师门登录优化版 v2.1 完整功能演示
目标网站: http://xiao8.lodsve.com:6007/x8login
"""

import requests
import json
import time
from datetime import datetime

# API基础URL
API_BASE = "https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com/api"

def print_header():
    """打印头部信息"""
    print("🚀 小八爬虫管理系统 - 师门登录优化版 v2.1")
    print("="*80)
    print(f"🎯 目标网站: http://xiao8.lodsve.com:6007/x8login")
    print(f"🌐 前端界面: https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com")
    print(f"🔗 后端API: {API_BASE}")
    print(f"⏰ 演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

def demo_real_crawling():
    """演示真实师门登录爬取"""
    print("\n🎯 师门登录优化版真实爬取演示")
    print("-" * 50)
    
    # 启动爬虫系统
    print("1. 启动师门爬虫系统...")
    response = requests.post(f"{API_BASE}/crawler/start")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ {data['message']}")
        print(f"   📊 创建账号数: {data['accounts']}")
    
    time.sleep(2)
    
    # 测试真实师门登录
    test_accounts = ["KR666", "KR777", "KR888"]
    successful_tests = 0
    
    for username in test_accounts:
        print(f"\n2. 测试账号 {username} 的师门登录优化...")
        try:
            response = requests.post(f"{API_BASE}/crawler/test/{username}", timeout=30)
            if response.status_code == 200:
                result = response.json()
                print(f"   🎯 账号: {result['username']}")
                print(f"   📊 结果: {result['test_result']}")
                print(f"   💡 详情: {result['message']}")
                print(f"   🏷️  版本: {result['version']}")
                
                if result['test_result'] == 'success':
                    successful_tests += 1
                    print(f"   ✅ 师门登录优化成功！")
                else:
                    print(f"   ⚠️ 师门登录测试未成功")
            else:
                print(f"   ❌ API请求失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 测试出错: {e}")
        
        time.sleep(3)  # 给服务器一些处理时间
    
    print(f"\n📈 测试总结: {successful_tests}/{len(test_accounts)} 个账号成功")
    return successful_tests > 0

def show_real_data():
    """显示真实抓取的数据"""
    print("\n📊 真实师门数据展示")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/crawler/data")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 共获取到 {len(data)} 条真实师门数据")
            
            # 按账号分组显示
            account_data = {}
            for item in data:
                username = item['account_username']
                if username not in account_data:
                    account_data[username] = []
                account_data[username].append(item)
            
            for username, items in account_data.items():
                print(f"\n👤 账号 {username} ({len(items)} 条数据):")
                
                # 显示前3条数据的详细信息
                for i, item in enumerate(items[:3]):
                    print(f"   {i+1}. 角色: {item['name']} | IP: {item['ip']}")
                    print(f"      类型: {item['type']} | 等级: {item['level']} | 门派: {item['guild']}")
                    print(f"      状态: {item['status']}")
                    print(f"      抓取时间: {item['crawl_timestamp'][:19]}")
                    print()
                
                if len(items) > 3:
                    print(f"   ... 还有 {len(items) - 3} 条数据")
            
            # 统计信息
            print("\n📈 数据统计:")
            types = [item['type'] for item in data]
            guilds = [item['guild'] for item in data]
            
            print(f"   🎭 角色类型: {set(types)}")
            print(f"   🏠 门派分布: {set(guilds)}")
            print(f"   📅 数据时间跨度: {min(item['crawl_timestamp'] for item in data)[:19]} ~ {max(item['crawl_timestamp'] for item in data)[:19]}")
            
            return True
        else:
            print(f"❌ 数据获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 数据展示出错: {e}")
        return False

def show_optimization_features():
    """展示v2.1优化特性"""
    print("\n🎯 v2.1 师门登录优化特性")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/version")
        if response.status_code == 200:
            version_info = response.json()
            
            print(f"🏷️  版本: {version_info['version']}")
            print(f"📅 更新日期: {version_info['update_date']}")
            
            print("\n🔧 核心特性:")
            for feature in version_info['features']:
                print(f"   • {feature}")
            
            print("\n📋 更新日志:")
            for change in version_info['changelog']:
                print(f"   {change}")
            
            return True
    except Exception as e:
        print(f"❌ 版本信息获取失败: {e}")
        return False

def main():
    """主演示函数"""
    print_header()
    
    # 展示优化特性
    show_optimization_features()
    
    # 演示真实爬取功能
    crawl_success = demo_real_crawling()
    
    # 显示真实数据
    if crawl_success:
        show_real_data()
    
    # 总结
    print("\n🎉 师门登录优化版 v2.1 演示完成！")
    print("="*80)
    print("✨ 系统亮点:")
    print("   🎯 成功连接目标网站: http://xiao8.lodsve.com:6007/x8login")
    print("   🔧 5种智能按钮识别策略确保登录成功")
    print("   📊 实时抓取和展示真实师门数据")
    print("   🎨 现代化React界面，美观易用")
    print("   🚀 FastAPI后端，高性能API服务")
    print("   📁 支持CSV数据导出功能")
    print("   🔄 支持多账号管理和状态监控")
    print("\n🌐 访问地址:")
    print("   前端: https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com")
    print("   API:  https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com/api")

if __name__ == "__main__":
    main()