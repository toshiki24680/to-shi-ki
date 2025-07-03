#!/usr/bin/env python3
"""
小八爬虫管理系统 - 师门登录优化版 v2.1 演示脚本
展示系统的主要功能和运行效果
"""

import requests
import json
import time
from datetime import datetime

# API基础URL
API_BASE = "https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com/api"

def print_section(title):
    """打印分节标题"""
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def print_success(message):
    """打印成功信息"""
    print(f"✅ {message}")

def print_info(message):
    """打印信息"""
    print(f"📋 {message}")

def demo_version_info():
    """演示版本信息"""
    print_section("小八爬虫系统版本信息")
    
    try:
        # 获取基本信息
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            data = response.json()
            print_info(f"系统名称: {data['message']}")
            print_info(f"版本: {data['version']}")
            print_info(f"架构: {data['architecture']}")
            print_info(f"更新时间: {data['update']}")
        
        # 获取详细版本信息
        response = requests.get(f"{API_BASE}/version")
        if response.status_code == 200:
            data = response.json()
            print_info(f"更新日期: {data['update_date']}")
            print_info("核心特性:")
            for feature in data['features']:
                print(f"    • {feature}")
            print_info("更新日志:")
            for change in data['changelog']:
                print(f"    {change}")
    
    except Exception as e:
        print(f"❌ 版本信息获取失败: {e}")

def demo_crawler_system():
    """演示爬虫系统功能"""
    print_section("师门爬虫系统启动和数据生成")
    
    try:
        # 启动爬虫系统
        print_info("启动师门爬虫系统...")
        response = requests.post(f"{API_BASE}/crawler/start")
        if response.status_code == 200:
            data = response.json()
            print_success(f"{data['message']}")
            print_info(f"已创建账号数: {data['accounts']}")
        
        time.sleep(1)
        
        # 生成演示数据
        print_info("生成师门演示数据...")
        response = requests.post(f"{API_BASE}/crawler/mock-data")
        if response.status_code == 200:
            data = response.json()
            print_success(f"{data['message']}")
    
    except Exception as e:
        print(f"❌ 爬虫系统操作失败: {e}")

def demo_accounts_data():
    """演示账号和数据管理"""
    print_section("师门账号和数据管理")
    
    try:
        # 获取账号列表
        print_info("获取师门账号列表...")
        response = requests.get(f"{API_BASE}/crawler/accounts")
        if response.status_code == 200:
            accounts = response.json()
            print_success(f"共 {len(accounts)} 个师门账号:")
            for acc in accounts:
                print(f"    • {acc['username']} - 状态: {acc['status']} - 创建时间: {acc['created_at'][:19]}")
        
        time.sleep(1)
        
        # 获取师门数据
        print_info("获取师门数据...")
        response = requests.get(f"{API_BASE}/crawler/data")
        if response.status_code == 200:
            data = response.json()
            print_success(f"共 {len(data)} 条师门数据:")
            
            # 按账号分组统计
            account_stats = {}
            for item in data:
                username = item['account_username']
                if username not in account_stats:
                    account_stats[username] = []
                account_stats[username].append(item)
            
            for username, items in account_stats.items():
                print(f"\n    📊 账号 {username} ({len(items)} 条记录):")
                for item in items[:2]:  # 只显示前两条
                    print(f"        - {item['name']} | {item['type']} | 等级{item['level']} | {item['guild']} | {item['status']}")
                if len(items) > 2:
                    print(f"        ... 还有 {len(items) - 2} 条记录")
    
    except Exception as e:
        print(f"❌ 账号数据获取失败: {e}")

def demo_system_status():
    """演示系统状态"""
    print_section("系统状态监控")
    
    try:
        response = requests.get(f"{API_BASE}/crawler/status")
        if response.status_code == 200:
            status = response.json()
            print_info("系统状态:")
            print(f"    🏠 总账号数: {status['total_accounts']}")
            print(f"    🔄 活跃账号: {status['active_accounts']}")
            print(f"    📊 总记录数: {status['total_records']}")
            print(f"    ⚡ 爬取状态: {status['crawl_status']}")
            print(f"    🖥️  系统信息: {status['system_info']}")
            print(f"    📅 最后更新: {status['last_update']}")
    
    except Exception as e:
        print(f"❌ 系统状态获取失败: {e}")

def demo_export_function():
    """演示导出功能"""
    print_section("数据导出功能")
    
    try:
        print_info("测试CSV导出功能...")
        response = requests.get(f"{API_BASE}/crawler/data/export")
        if response.status_code == 200:
            print_success("CSV导出功能正常!")
            print_info(f"导出内容类型: {response.headers.get('Content-Type', '未知')}")
            print_info(f"导出文件大小: {len(response.content)} 字节")
            
            # 显示前几行内容（如果是文本格式）
            try:
                content = response.content.decode('utf-8-sig')
                lines = content.split('\n')[:5]
                print_info("导出内容预览:")
                for line in lines:
                    if line.strip():
                        print(f"    {line}")
            except:
                print_info("导出内容为二进制格式")
    
    except Exception as e:
        print(f"❌ 导出功能测试失败: {e}")

def demo_optimization_test():
    """演示师门登录优化测试"""
    print_section("师门登录优化测试")
    
    try:
        # 测试一个账号的师门登录优化
        test_username = "KR666"
        print_info(f"测试账号 {test_username} 的师门登录优化功能...")
        
        response = requests.post(f"{API_BASE}/crawler/test/{test_username}")
        if response.status_code == 200:
            result = response.json()
            print_info(f"测试账号: {result['username']}")
            print_info(f"测试结果: {result['test_result']}")
            print_info(f"版本: {result['version']}")
            print_info(f"登录类型: {result['login_type']}")
            print_info(f"详情: {result['message']}")
            
            if result['test_result'] == 'success':
                print_success("师门登录优化测试成功!")
            else:
                print_info("师门登录优化测试失败（这可能是正常的，因为测试环境限制）")
    
    except Exception as e:
        print(f"❌ 师门登录优化测试失败: {e}")

def main():
    """主演示函数"""
    print("🚀 小八爬虫管理系统 - 师门登录优化版 v2.1")
    print("功能演示和运行效果展示")
    print(f"演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 依次演示各个功能模块
    demo_version_info()
    time.sleep(2)
    
    demo_crawler_system()
    time.sleep(2)
    
    demo_accounts_data()
    time.sleep(2)
    
    demo_system_status()
    time.sleep(2)
    
    demo_export_function()
    time.sleep(2)
    
    demo_optimization_test()
    
    print_section("演示完成")
    print_success("小八爬虫管理系统 v2.1 师门登录优化版演示完成!")
    print_info("前端界面地址: https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com")
    print_info("后端API地址: https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com/api")
    print("\n🎯 主要功能:")
    print("  • 师门登录流程优化（5种按钮识别策略）")
    print("  • 账号管理和数据监控")
    print("  • 实时数据展示和导出")
    print("  • 美观的现代化UI界面")
    print("  • 完整的API接口")

if __name__ == "__main__":
    main()