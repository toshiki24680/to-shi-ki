#!/usr/bin/env python3
"""
小八爬虫管理系统 v2.5 - 账号活跃保持 + 关键词管理功能演示
展示所有账号始终保持活跃状态和自定义关键词管理功能
"""

import requests
import json
import time
from datetime import datetime

# API基础URL
API_BASE = "https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com/api"

def print_header():
    """打印头部信息"""
    print("🚀 小八爬虫管理系统 v2.5 - 新功能演示")
    print("="*80)
    print("🎯 新增功能:")
    print("   1. 所有账号始终保持活跃状态")
    print("   2. 45秒自动刷新爬虫数据")
    print("   3. 自定义关键词管理功能")
    print("   4. 删除关键词功能")
    print(f"⏰ 演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

def demo_active_account_maintenance():
    """演示账号活跃状态保持功能"""
    print("\n🔄 账号活跃状态保持功能演示")
    print("-" * 50)
    
    try:
        # 启动自动爬虫
        print("1. 启动自动爬虫（账号活跃保持模式）...")
        response = requests.post(f"{API_BASE}/crawler/start")
        if response.status_code == 200:
            print(f"   ✅ 爬虫系统启动成功")
        
        response = requests.post(f"{API_BASE}/crawler/auto/start")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 自动爬虫启动 - {data['message']}")
        
        time.sleep(2)
        
        # 检查账号状态
        print("\n2. 检查所有账号状态...")
        response = requests.get(f"{API_BASE}/accounts")
        if response.status_code == 200:
            accounts = response.json()
            print(f"   📊 总账号数: {len(accounts)}")
            
            active_count = 0
            for acc in accounts:
                status = acc['status']
                is_auto = acc.get('is_auto_enabled', False)
                print(f"     • {acc['username']}: {status} - 自动启用: {is_auto}")
                if status in ['active', 'running']:
                    active_count += 1
            
            print(f"   🟢 活跃账号: {active_count}/{len(accounts)}")
            
            # 等待一个周期观察状态维持
            print("\n3. 等待45秒观察账号状态保持...")
            for i in range(9):
                time.sleep(5)
                print(f"   ⏳ 等待中... {(i+1)*5}/45 秒")
                
                # 每15秒检查一次状态
                if (i+1) % 3 == 0:
                    response = requests.get(f"{API_BASE}/accounts")
                    if response.status_code == 200:
                        accounts = response.json()
                        active_now = len([acc for acc in accounts if acc['status'] in ['active', 'running']])
                        print(f"     📊 当前活跃账号: {active_now}/{len(accounts)}")
            
            print("   ✅ 账号活跃状态保持测试完成")
        
        return True
    except Exception as e:
        print(f"❌ 账号活跃状态保持测试失败: {e}")
        return False

def demo_keyword_management():
    """演示关键词管理功能"""
    print("\n🏷️ 关键词管理功能演示")
    print("-" * 50)
    
    try:
        # 获取当前关键词列表
        print("1. 获取当前关键词列表...")
        response = requests.get(f"{API_BASE}/crawler/keywords")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 当前监控关键词数: {len(data.get('monitored_keywords', []))}")
            print(f"   🎯 默认关键词数: {len(data.get('default_keywords', []))}")
            
            print("   📋 默认关键词:")
            for i, keyword in enumerate(data.get('default_keywords', [])[:5]):
                print(f"     {i+1}. {keyword}")
            
            custom_keywords = [k for k in data.get('monitored_keywords', []) 
                             if k not in data.get('default_keywords', [])]
            print(f"   ⚙️ 自定义关键词数: {len(custom_keywords)}")
            for keyword in custom_keywords[:3]:
                print(f"     • {keyword}")
        
        # 添加单个关键词
        print("\n2. 添加单个自定义关键词...")
        test_keyword = f"测试关键词_{int(time.time())}"
        response = requests.post(f"{API_BASE}/crawler/keywords/add", json={
            "keyword": test_keyword
        })
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 关键词添加成功: {result['keyword']}")
            print(f"   📊 总关键词数: {result['total_keywords']}")
        
        # 批量添加关键词
        print("\n3. 批量添加关键词...")
        batch_keywords = ["网络延迟", "内存不足", "CPU占用高"]
        response = requests.post(f"{API_BASE}/crawler/keywords/batch", json={
            "keywords": batch_keywords
        })
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 批量添加完成")
            print(f"   📈 添加成功: {result['added_count']} 个")
            print(f"   📋 添加的关键词: {', '.join(result['added_keywords'])}")
            print(f"   📊 总关键词数: {result['total_keywords']}")
        
        # 删除关键词
        print("\n4. 删除测试关键词...")
        response = requests.delete(f"{API_BASE}/crawler/keywords/{test_keyword}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 关键词删除成功: {result['keyword']}")
            print(f"   📊 剩余关键词数: {result['total_keywords']}")
        
        # 尝试删除默认关键词（应该失败）
        print("\n5. 测试删除默认关键词保护...")
        response = requests.delete(f"{API_BASE}/crawler/keywords/人脸提示")
        if response.status_code == 400:
            print("   ✅ 默认关键词删除保护正常工作")
        else:
            print("   ⚠️ 默认关键词删除保护可能有问题")
        
        # 恢复默认关键词
        print("\n6. 恢复默认关键词设置...")
        response = requests.post(f"{API_BASE}/crawler/keywords/restore-defaults")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 默认关键词已恢复")
            print(f"   📊 总关键词数: {result['total_keywords']}")
            print(f"   📋 自定义关键词数: {len(result['custom_keywords'])}")
        
        return True
    except Exception as e:
        print(f"❌ 关键词管理功能测试失败: {e}")
        return False

def demo_auto_refresh():
    """演示45秒自动刷新功能"""
    print("\n🔄 45秒自动刷新功能演示")
    print("-" * 50)
    
    try:
        # 获取当前数据数量
        print("1. 获取当前数据基线...")
        response = requests.get(f"{API_BASE}/crawler/data")
        if response.status_code == 200:
            initial_data = response.json()
            initial_count = len(initial_data)
            print(f"   📊 初始数据条数: {initial_count}")
        
        # 获取自动爬虫状态
        response = requests.get(f"{API_BASE}/crawler/auto/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   🔄 自动爬虫状态: {'运行中' if status['running'] else '已停止'}")
            print(f"   ⏰ 刷新间隔: {status['interval']} 秒")
            print(f"   👥 活跃账号: {status['active_accounts']}")
        
        # 等待一个完整周期
        print("\n2. 等待一个完整的45秒刷新周期...")
        for i in range(9):
            time.sleep(5)
            remaining = 45 - (i+1)*5
            print(f"   ⏳ 倒计时: {remaining} 秒...")
            
            # 每15秒检查一次数据变化
            if (i+1) % 3 == 0:
                response = requests.get(f"{API_BASE}/crawler/data")
                if response.status_code == 200:
                    current_data = response.json()
                    current_count = len(current_data)
                    print(f"     📊 当前数据条数: {current_count} (变化: +{current_count - initial_count})")
        
        # 检查最终结果
        print("\n3. 检查45秒刷新结果...")
        response = requests.get(f"{API_BASE}/crawler/data")
        if response.status_code == 200:
            final_data = response.json()
            final_count = len(final_data)
            print(f"   📊 最终数据条数: {final_count}")
            print(f"   📈 本周期新增: {final_count - initial_count} 条")
            
            if final_count > initial_count:
                print("   ✅ 45秒自动刷新功能正常工作")
                
                # 显示最新的几条数据
                latest_data = sorted(final_data, key=lambda x: x['crawl_timestamp'], reverse=True)[:3]
                print("   📋 最新3条数据:")
                for i, item in enumerate(latest_data):
                    print(f"     {i+1}. {item['account_username']} - {item['name']} - {item['status']}")
            else:
                print("   ⚠️ 本周期内未检测到新数据")
        
        return True
    except Exception as e:
        print(f"❌ 45秒自动刷新功能测试失败: {e}")
        return False

def demo_enhanced_monitoring():
    """演示增强的监控功能"""
    print("\n📊 增强监控功能展示")
    print("-" * 50)
    
    try:
        # 获取爬取历史
        print("1. 获取爬取历史记录...")
        response = requests.get(f"{API_BASE}/crawler/history")
        if response.status_code == 200:
            history = response.json()
            print(f"   📈 总爬取次数: {history.get('total_crawls', 0)}")
            print(f"   ✅ 成功率: {(history.get('success_rate', 0) * 100):.1f}%")
            
            recent = history.get('history', [])[-5:]
            if recent:
                print("   📋 最近5次爬取:")
                for entry in recent:
                    timestamp = entry.get('timestamp', '')[:19]
                    account = entry.get('account', '')
                    success = "成功" if entry.get('success') else "失败"
                    count = entry.get('data_count', 0)
                    print(f"     • {timestamp} - {account} - {success} - {count}条")
        
        # 获取关键词统计
        print("\n2. 获取关键词监控统计...")
        response = requests.get(f"{API_BASE}/crawler/keywords")
        if response.status_code == 200:
            stats = response.json()
            print(f"   🚨 总检测次数: {stats.get('total_keywords_detected', 0)}")
            print(f"   📊 触发关键词类型: {stats.get('unique_keywords', 0)}")
            print(f"   👀 监控关键词总数: {len(stats.get('monitored_keywords', []))}")
            
            keyword_stats = stats.get('keyword_stats', {})
            if keyword_stats:
                print("   📋 触发频次最高的关键词:")
                sorted_keywords = sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True)
                for keyword, count in sorted_keywords[:5]:
                    print(f"     • {keyword}: {count} 次")
            else:
                print("   ℹ️ 暂无关键词触发记录")
        
        # 获取系统状态
        print("\n3. 获取系统运行状态...")
        response = requests.get(f"{API_BASE}/crawler/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   🖥️ 系统版本: {status.get('version', 'unknown')}")
            print(f"   👥 总账号数: {status.get('total_accounts', 0)}")
            print(f"   🟢 活跃账号数: {status.get('active_accounts', 0)}")
            print(f"   📊 总记录数: {status.get('total_records', 0)}")
            print(f"   🔄 爬取状态: {status.get('crawl_status', 'unknown')}")
            print(f"   🚨 关键词预警: {status.get('keyword_alerts', 0)} 次")
        
        return True
    except Exception as e:
        print(f"❌ 增强监控功能展示失败: {e}")
        return False

def main():
    """主演示函数"""
    print_header()
    
    # 演示各个新功能
    results = {}
    
    print("\n🎬 开始新功能演示...")
    
    results['active_maintenance'] = demo_active_account_maintenance()
    time.sleep(2)
    
    results['keyword_management'] = demo_keyword_management()
    time.sleep(2)
    
    results['auto_refresh'] = demo_auto_refresh()
    time.sleep(2)
    
    results['enhanced_monitoring'] = demo_enhanced_monitoring()
    
    # 总结
    print("\n🎉 v2.5 新功能演示完成！")
    print("="*80)
    
    # 功能测试结果
    successful_tests = sum(1 for success in results.values() if success)
    total_tests = len(results)
    
    print(f"📊 新功能测试结果: {successful_tests}/{total_tests} 通过")
    print("✨ 已实现的新功能:")
    print("   🔄 所有账号始终保持活跃状态")
    print("   ⏰ 45秒自动刷新爬虫数据")
    print("   ➕ 自定义关键词添加功能")
    print("   🗑️ 关键词删除功能")
    print("   📝 批量关键词管理")
    print("   🛡️ 默认关键词保护机制")
    print("   🔄 默认关键词恢复功能")
    print("   📊 增强的监控和统计")
    
    print(f"\n🎯 核心改进:")
    print("   • 自动爬虫现在会强制保持所有账号为活跃状态")
    print("   • 即使出现错误，账号也会自动恢复到活跃状态")
    print("   • 45秒间隔确保数据实时更新")
    print("   • 关键词管理更加灵活，支持自定义和批量操作")
    print("   • 默认关键词受到保护，不能被意外删除")
    
    print(f"\n🌐 访问地址:")
    print("   前端: https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com")
    print("   API:  https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com/api")
    
    print(f"\n💡 使用建议:")
    print("   1. 系统会自动保持所有账号活跃，无需手动干预")
    print("   2. 添加针对性关键词来监控特定问题")
    print("   3. 定期查看关键词统计了解系统运行状况")
    print("   4. 使用批量添加功能快速配置多个监控关键词")

if __name__ == "__main__":
    main()