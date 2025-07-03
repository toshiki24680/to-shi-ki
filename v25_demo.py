#!/usr/bin/env python3
"""
小八爬虫管理系统 v2.5 自动化增强版 - 完整功能演示
展示45秒自动爬虫、多账号管理、数据累计、关键词统计等功能
"""

import requests
import json
import time
from datetime import datetime

# API基础URL
API_BASE = "https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com/api"

def print_header():
    """打印头部信息"""
    print("🚀 小八爬虫管理系统 v2.5 - 自动化增强版")
    print("="*80)
    print(f"🎯 目标网站: http://xiao8.lodsve.com:6007/x8login")
    print(f"🌐 前端界面: https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com")
    print(f"🔗 后端API: {API_BASE}")
    print(f"⏰ 演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

def demo_version_upgrade():
    """演示版本升级信息"""
    print("\n🎯 版本升级信息 v2.1 → v2.5")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/version")
        if response.status_code == 200:
            version_info = response.json()
            
            print(f"✅ 当前版本: v{version_info['version']}")
            print(f"📅 更新日期: {version_info['update_date']}")
            
            print(f"\n🔧 新增功能特性:")
            for feature in version_info['features']:
                print(f"    • {feature}")
            
            print(f"\n📋 版本更新日志:")
            for change in version_info['changelog']:
                print(f"    {change}")
            
            return True
    except Exception as e:
        print(f"❌ 版本信息获取失败: {e}")
        return False

def demo_auto_crawler():
    """演示45秒自动爬虫功能"""
    print("\n🤖 45秒自动爬虫功能演示")
    print("-" * 50)
    
    try:
        # 启动自动爬虫
        print("1. 启动45秒自动爬虫...")
        response = requests.post(f"{API_BASE}/crawler/auto/start")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data['message']}")
            print(f"   ⏰ 爬取间隔: {data['interval']}")
        
        time.sleep(2)
        
        # 检查自动爬虫状态
        print("\n2. 检查自动爬虫状态...")
        response = requests.get(f"{API_BASE}/crawler/auto/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   🔄 运行状态: {'运行中' if status['running'] else '已停止'}")
            print(f"   ⏱️  爬取间隔: {status['interval']} 秒")
            print(f"   👥 总账号数: {status['total_accounts']}")
            print(f"   🟢 活跃账号: {status['active_accounts']}")
            print(f"   📊 历史记录: {status['crawl_history_count']} 条")
        
        print("\n3. 等待一个周期观察自动运行...")
        print("   🕐 等待中... (可在前端界面观察实时状态)")
        time.sleep(10)
        
        # 再次检查状态变化
        response = requests.get(f"{API_BASE}/crawler/auto/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ 自动爬虫仍在运行: {status['running']}")
        
        return True
    except Exception as e:
        print(f"❌ 自动爬虫功能测试失败: {e}")
        return False

def demo_account_management():
    """演示多账号管理功能"""
    print("\n👥 多账号管理功能演示")
    print("-" * 50)
    
    try:
        # 获取现有账号
        print("1. 获取现有账号列表...")
        response = requests.get(f"{API_BASE}/accounts")
        if response.status_code == 200:
            accounts = response.json()
            print(f"   📊 当前账号数: {len(accounts)}")
            for acc in accounts[:3]:  # 显示前3个
                print(f"     • {acc['username']} - 状态: {acc['status']} - 自动启用: {acc.get('is_auto_enabled', True)}")
        
        # 添加新账号
        print("\n2. 添加新测试账号...")
        new_account = {
            "username": f"TEST_{int(time.time())}",
            "password": "test123",
            "preferred_guild": "测试门派"
        }
        
        response = requests.post(f"{API_BASE}/accounts", json=new_account)
        if response.status_code == 200:
            created_account = response.json()
            print(f"   ✅ 账号创建成功: {created_account['username']}")
            account_id = created_account['id']
            
            # 更新账号信息
            print("\n3. 更新账号设置...")
            update_data = {"is_auto_enabled": False, "status": "paused"}
            response = requests.put(f"{API_BASE}/accounts/{account_id}", json=update_data)
            if response.status_code == 200:
                print("   ✅ 账号更新成功")
            
            # 批量操作演示
            print("\n4. 批量操作演示...")
            batch_data = {
                "account_ids": [account_id],
                "operation": "stop"
            }
            response = requests.post(f"{API_BASE}/accounts/batch", json=batch_data)
            if response.status_code == 200:
                print("   ✅ 批量停止操作成功")
            
            # 删除测试账号
            print("\n5. 删除测试账号...")
            response = requests.delete(f"{API_BASE}/accounts/{account_id}")
            if response.status_code == 200:
                print("   ✅ 测试账号删除成功")
        
        return True
    except Exception as e:
        print(f"❌ 账号管理功能测试失败: {e}")
        return False

def demo_data_features():
    """演示数据累计和筛选功能"""
    print("\n📊 数据累计和筛选功能演示")
    print("-" * 50)
    
    try:
        # 生成测试数据
        print("1. 生成师门测试数据...")
        response = requests.post(f"{API_BASE}/crawler/mock-data")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data['message']}")
        
        # 获取统计信息
        print("\n2. 获取数据统计分析...")
        response = requests.get(f"{API_BASE}/crawler/stats")
        if response.status_code == 200:
            stats = response.json()
            
            basic = stats.get('basic_stats', {})
            accumulation = stats.get('accumulation_stats', {})
            
            print("   📈 基础统计:")
            print(f"     • 总记录数: {basic.get('total_records', 0)}")
            print(f"     • 独立账号: {basic.get('unique_accounts', 0)}")
            print(f"     • 不同门派: {basic.get('unique_guilds', 0)}")
            print(f"     • 平均等级: {basic.get('avg_level', 0):.1f}")
            
            print("   🔄 累计数据统计:")
            print(f"     • 总累计次数: {accumulation.get('total_accumulated_count', 0)}")
            print(f"     • 总重置周期: {accumulation.get('total_cycles', 0)}")
            print(f"     • 平均累计/记录: {accumulation.get('avg_accumulated_per_record', 0):.2f}")
        
        # 数据筛选演示
        print("\n3. 数据筛选功能演示...")
        filter_data = {
            "guild": "普陀山",
            "min_level": 80,
            "max_level": 120
        }
        
        response = requests.post(f"{API_BASE}/crawler/data/filter", json=filter_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   🔍 筛选结果: 从 {result.get('total_count', 0)} 条记录中筛选出 {result.get('filtered_count', 0)} 条")
            print(f"   📋 筛选条件: 门派=普陀山, 等级=80-120")
        
        return True
    except Exception as e:
        print(f"❌ 数据功能测试失败: {e}")
        return False

def demo_keyword_monitoring():
    """演示关键词统计功能"""
    print("\n🚨 关键词监控功能演示")
    print("-" * 50)
    
    try:
        # 获取关键词统计
        print("1. 获取关键词监控统计...")
        response = requests.get(f"{API_BASE}/crawler/keywords")
        if response.status_code == 200:
            stats = response.json()
            
            print(f"   📊 总检测次数: {stats.get('total_keywords_detected', 0)}")
            print(f"   🎯 触发关键词数: {stats.get('unique_keywords', 0)}")
            print(f"   👀 监控关键词: {len(stats.get('monitored_keywords', []))}")
            
            print("   🔍 监控关键词列表:")
            for keyword in stats.get('monitored_keywords', [])[:5]:  # 显示前5个
                count = stats.get('keyword_stats', {}).get(keyword, 0)
                print(f"     • {keyword}: {count} 次")
        
        # 重置关键词统计
        print("\n2. 重置关键词统计...")
        response = requests.post(f"{API_BASE}/crawler/keywords/reset")
        if response.status_code == 200:
            print("   ✅ 关键词统计已重置")
        
        return True
    except Exception as e:
        print(f"❌ 关键词监控功能测试失败: {e}")
        return False

def demo_crawl_history():
    """演示爬取历史功能"""
    print("\n📈 爬取历史功能演示")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/crawler/history")
        if response.status_code == 200:
            history = response.json()
            
            print(f"   📊 总爬取次数: {history.get('total_crawls', 0)}")
            print(f"   ✅ 成功率: {(history.get('success_rate', 0) * 100):.1f}%")
            
            recent_history = history.get('history', [])[-5:]  # 最近5条
            if recent_history:
                print("   📋 最近爬取记录:")
                for entry in recent_history:
                    status = "成功" if entry.get('success') else "失败"
                    print(f"     • {entry.get('account')} - {status} - {entry.get('data_count', 0)} 条数据 - {entry.get('timestamp', '')[:19]}")
        
        return True
    except Exception as e:
        print(f"❌ 爬取历史功能测试失败: {e}")
        return False

def demo_export_function():
    """演示增强的导出功能"""
    print("\n📁 增强CSV导出功能演示")
    print("-" * 50)
    
    try:
        print("1. 测试增强CSV导出...")
        response = requests.get(f"{API_BASE}/crawler/data/export")
        if response.status_code == 200:
            print(f"   ✅ CSV导出成功")
            print(f"   📊 文件大小: {len(response.content)} 字节")
            print(f"   📋 内容类型: {response.headers.get('Content-Type', '未知')}")
            
            # 尝试解析CSV内容预览
            try:
                content = response.content.decode('utf-8-sig')
                lines = content.split('\n')[:3]
                print("   📄 内容预览:")
                for line in lines:
                    if line.strip():
                        print(f"     {line}")
            except Exception:
                print("   📄 导出文件为二进制格式")
        
        return True
    except Exception as e:
        print(f"❌ 导出功能测试失败: {e}")
        return False

def demo_frontend_features():
    """演示前端界面特性"""
    print("\n🎨 前端界面特性展示")
    print("-" * 50)
    
    frontend_url = "https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com"
    
    print("✨ 全新5标签页界面设计:")
    print(f"   🏠 数据面板 - 实时显示爬虫数据和状态")
    print(f"   🔍 数据筛选 - 多维度筛选和搜索功能")
    print(f"   👥 账号管理 - 完整的账号CRUD操作和批量控制")
    print(f"   📊 统计分析 - 数据摘要和性能分析")
    print(f"   🚨 关键词统计 - 异常关键词监控和统计")
    
    print(f"\n🌐 前端访问地址: {frontend_url}")
    print("🎯 界面特点:")
    print("   • 现代化渐变色设计")
    print("   • 响应式布局，适配各种屏幕")
    print("   • 实时数据更新，30秒自动刷新")
    print("   • 直观的状态指示器和进度条")
    print("   • 交互式数据表格和筛选器")

def main():
    """主演示函数"""
    print_header()
    
    # 演示各个功能模块
    results = {}
    
    print("\n🎬 开始功能演示...")
    
    results['version'] = demo_version_upgrade()
    time.sleep(1)
    
    results['auto_crawler'] = demo_auto_crawler()
    time.sleep(1)
    
    results['account_mgmt'] = demo_account_management()
    time.sleep(1)
    
    results['data_features'] = demo_data_features()
    time.sleep(1)
    
    results['keyword_monitoring'] = demo_keyword_monitoring()
    time.sleep(1)
    
    results['crawl_history'] = demo_crawl_history()
    time.sleep(1)
    
    results['export'] = demo_export_function()
    time.sleep(1)
    
    demo_frontend_features()
    
    # 总结
    print("\n🎉 v2.5 自动化增强版演示完成！")
    print("="*80)
    
    # 功能测试结果
    successful_tests = sum(1 for success in results.values() if success)
    total_tests = len(results)
    
    print(f"📊 功能测试结果: {successful_tests}/{total_tests} 通过")
    print("✨ 新功能亮点:")
    print("   🤖 45秒自动爬虫 - 持续监控师门状态")
    print("   👥 完整账号管理 - 添加/删除/批量操作")
    print("   🔄 数据累计逻辑 - 智能检测重置周期")
    print("   🚨 关键词监控 - 实时检测异常状态")
    print("   📊 数据筛选分析 - 多维度数据挖掘")
    print("   📁 增强CSV导出 - 包含累计数据统计")
    print("   🎨 全新UI界面 - 5标签页专业设计")
    
    print(f"\n🌐 立即体验:")
    print("   前端: https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com")
    print("   API:  https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com/api")
    
    print(f"\n🎯 建议操作:")
    print("   1. 访问前端界面体验5个功能标签页")
    print("   2. 启动45秒自动爬虫观察实时效果")
    print("   3. 在账号管理页面添加/删除账号")
    print("   4. 使用数据筛选功能进行多维度分析")
    print("   5. 查看统计分析了解系统运行状况")

if __name__ == "__main__":
    main()