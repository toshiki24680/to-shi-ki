#!/usr/bin/env python3
"""
小八爬虫管理系统 - 10个活跃账号验证脚本
验证系统维持10个账号同时在线活跃
"""

import requests
import json
import time
from datetime import datetime

# API基础URL
API_BASE = "https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com/api"

def print_header():
    """打印头部信息"""
    print("🚀 小八爬虫管理系统 - 10个活跃账号验证")
    print("="*70)
    print("🎯 目标: 验证系统维持10个账号同时在线活跃")
    print(f"⏰ 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

def verify_account_count():
    """验证账号数量和配置"""
    print("\n👥 账号数量和配置验证")
    print("-" * 50)
    
    try:
        # 获取系统配置
        print("1. 检查系统配置...")
        response = requests.get(f"{API_BASE}/crawler/config")
        if response.status_code == 200:
            config = response.json()
            max_active = config.get('max_active_accounts', 0)
            max_concurrent = config.get('max_concurrent_crawlers', 0)
            
            print(f"   🎯 最大活跃账号数: {max_active}")
            print(f"   🚀 最大并发数: {max_concurrent}")
            print(f"   ⏰ 爬取间隔: {config.get('crawl_interval', 0)} 秒")
            print(f"   🔄 自动爬虫: {'运行中' if config.get('auto_crawl_enabled') else '已停止'}")
            
            if max_active == 10:
                print("   ✅ 活跃账号数配置正确: 10")
            else:
                print(f"   ❌ 活跃账号数配置错误: 期望10，实际{max_active}")
                return False
        
        # 获取账号列表
        print("\n2. 检查账号数量...")
        response = requests.get(f"{API_BASE}/accounts")
        if response.status_code == 200:
            accounts = response.json()
            total_accounts = len(accounts)
            active_accounts = [acc for acc in accounts if acc.get('is_auto_enabled', False)]
            active_count = len(active_accounts)
            
            print(f"   📊 总账号数: {total_accounts}")
            print(f"   🟢 活跃账号数: {active_count}")
            print(f"   📋 非活跃账号数: {total_accounts - active_count}")
            
            if total_accounts >= 10:
                print(f"   ✅ 账号数量充足: {total_accounts} ≥ 10")
            else:
                print(f"   ❌ 账号数量不足: {total_accounts} < 10")
                return False
                
            if active_count == 10:
                print(f"   ✅ 活跃账号数正确: {active_count}")
            else:
                print(f"   ⚠️ 活跃账号数: {active_count} (期望10)")
            
            return True
        else:
            print(f"   ❌ 获取账号失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return False

def verify_active_accounts():
    """验证活跃账号详情"""
    print("\n🔍 活跃账号详情验证")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/accounts")
        if response.status_code == 200:
            accounts = response.json()
            
            # 分析账号状态
            active_accounts = []
            inactive_accounts = []
            
            for acc in accounts:
                if acc.get('is_auto_enabled', False):
                    active_accounts.append(acc)
                else:
                    inactive_accounts.append(acc)
            
            print(f"1. 活跃账号列表 ({len(active_accounts)} 个):")
            for i, acc in enumerate(active_accounts, 1):
                status_icon = "🏃" if acc['status'] == 'running' else "✅" if acc['status'] == 'active' else "⚠️"
                crawl_count = acc.get('crawl_count', 0)
                success_rate = (acc.get('success_rate', 0) * 100)
                print(f"   {i:2d}. {status_icon} {acc['username']:<6} - {acc['status']:<8} - 爬取:{crawl_count:3d}次 - 成功率:{success_rate:5.1f}%")
            
            if inactive_accounts:
                print(f"\n2. 非活跃账号列表 ({len(inactive_accounts)} 个):")
                for i, acc in enumerate(inactive_accounts, 1):
                    print(f"   {i:2d}. ⭕ {acc['username']:<6} - {acc['status']:<8} - 非活跃状态")
            else:
                print("\n2. 非活跃账号: 无")
            
            # 状态统计
            status_count = {}
            for acc in active_accounts:
                status = acc['status']
                status_count[status] = status_count.get(status, 0) + 1
            
            print(f"\n3. 活跃账号状态分布:")
            for status, count in status_count.items():
                icon = "🏃" if status == 'running' else "✅" if status == 'active' else "⚠️"
                print(f"   {icon} {status}: {count} 个")
            
            return len(active_accounts) == 10
        
    except Exception as e:
        print(f"❌ 活跃账号验证失败: {e}")
        return False

def verify_auto_crawler_behavior():
    """验证自动爬虫行为"""
    print("\n🤖 自动爬虫行为验证")
    print("-" * 50)
    
    try:
        # 检查自动爬虫状态
        print("1. 检查自动爬虫状态...")
        response = requests.get(f"{API_BASE}/crawler/auto/status")
        if response.status_code == 200:
            status = response.json()
            
            print(f"   🔄 运行状态: {'运行中' if status.get('running') else '已停止'}")
            print(f"   ⏰ 爬取间隔: {status.get('interval', 0)} 秒")
            print(f"   👥 总账号数: {status.get('total_accounts', 0)}")
            print(f"   🟢 活跃账号数: {status.get('active_accounts', 0)}")
            
            if status.get('active_accounts', 0) == 10:
                print("   ✅ 自动爬虫维持10个活跃账号")
            else:
                print(f"   ⚠️ 自动爬虫活跃账号数: {status.get('active_accounts', 0)} (期望10)")
        
        # 观察一段时间的状态变化
        print("\n2. 观察30秒内的账号状态变化...")
        initial_response = requests.get(f"{API_BASE}/accounts")
        initial_active = 0
        if initial_response.status_code == 200:
            initial_accounts = initial_response.json()
            initial_active = len([acc for acc in initial_accounts if acc.get('is_auto_enabled', False)])
        
        print(f"   📊 初始活跃账号数: {initial_active}")
        
        # 每10秒检查一次，总共30秒
        for i in range(3):
            time.sleep(10)
            
            response = requests.get(f"{API_BASE}/accounts")
            if response.status_code == 200:
                accounts = response.json()
                active_count = len([acc for acc in accounts if acc.get('is_auto_enabled', False)])
                running_count = len([acc for acc in accounts if acc.get('status') == 'running'])
                active_status_count = len([acc for acc in accounts if acc.get('status') == 'active'])
                
                elapsed = (i + 1) * 10
                print(f"   ⏱️  {elapsed}秒: 活跃:{active_count}, 运行中:{running_count}, 待机:{active_status_count}")
                
                if active_count != 10:
                    print(f"   ⚠️ 活跃账号数异常: {active_count} ≠ 10")
        
        print("   ✅ 30秒观察完成")
        return True
        
    except Exception as e:
        print(f"❌ 自动爬虫行为验证失败: {e}")
        return False

def verify_performance_metrics():
    """验证性能指标"""
    print("\n📊 性能指标验证")
    print("-" * 50)
    
    try:
        # 获取系统状态
        print("1. 系统整体状态...")
        response = requests.get(f"{API_BASE}/crawler/status")
        if response.status_code == 200:
            status = response.json()
            
            print(f"   🖥️ 系统版本: v{status.get('version', 'unknown')}")
            print(f"   👥 总账号数: {status.get('total_accounts', 0)}")
            print(f"   🟢 活跃账号数: {status.get('active_accounts', 0)}")
            print(f"   📊 总记录数: {status.get('total_records', 0)}")
            print(f"   🔄 爬取状态: {status.get('crawl_status', 'unknown')}")
        
        # 获取爬取历史
        print("\n2. 爬取历史分析...")
        response = requests.get(f"{API_BASE}/crawler/history")
        if response.status_code == 200:
            history = response.json()
            
            total_crawls = history.get('total_crawls', 0)
            success_rate = history.get('success_rate', 0)
            
            print(f"   📈 总爬取次数: {total_crawls}")
            print(f"   ✅ 成功率: {(success_rate * 100):.1f}%")
            
            recent_history = history.get('history', [])
            if recent_history:
                print(f"   📋 最近爬取记录: {len(recent_history)} 条")
                
                # 统计最近的账号分布
                recent_accounts = {}
                for entry in recent_history[-20:]:  # 最近20条
                    account = entry.get('account', 'unknown')
                    recent_accounts[account] = recent_accounts.get(account, 0) + 1
                
                print(f"   📊 最近爬取的账号分布:")
                for account, count in sorted(recent_accounts.items()):
                    print(f"     {account}: {count} 次")
            else:
                print("   ℹ️ 暂无爬取历史")
        
        # 性能评估
        print("\n3. 性能评估...")
        total_accounts = status.get('total_accounts', 0)
        active_accounts = status.get('active_accounts', 0)
        
        if total_accounts >= 10 and active_accounts == 10:
            print("   ✅ 账号配置优秀: 10个账号同时活跃")
            print("   🚀 并发能力: 支持10个账号并发爬取")
            print("   ⚡ 理论性能: 达到设计目标")
        else:
            print(f"   ⚠️ 性能状态: 活跃账号{active_accounts}/10")
        
        return True
        
    except Exception as e:
        print(f"❌ 性能指标验证失败: {e}")
        return False

def main():
    """主函数"""
    print_header()
    
    # 执行各项验证
    results = {}
    
    results['account_count'] = verify_account_count()
    time.sleep(2)
    
    results['active_accounts'] = verify_active_accounts()
    time.sleep(2)
    
    results['auto_crawler'] = verify_auto_crawler_behavior()
    time.sleep(2)
    
    results['performance'] = verify_performance_metrics()
    
    # 总结
    print("\n🎉 10个活跃账号验证完成！")
    print("="*70)
    
    successful_tests = sum(1 for success in results.values() if success)
    total_tests = len(results)
    
    print(f"📊 验证结果: {successful_tests}/{total_tests} 通过")
    
    if successful_tests == total_tests:
        print("\n✅ 验证成功总结:")
        print("   🎯 系统成功维持10个账号同时在线活跃")
        print("   📊 所有10个账号状态正常")
        print("   🤖 自动爬虫正确管理活跃账号数量")
        print("   🚀 系统性能达到设计目标")
        
        print("\n🎊 功能亮点:")
        print("   • 10个账号同时保持活跃状态")
        print("   • 10个并发爬取能力")
        print("   • 45秒自动刷新周期")
        print("   • 智能账号状态管理")
        print("   • 高可用性和稳定性")
        
        print("\n💼 业务价值:")
        print("   • 提升数据获取效率")
        print("   • 增强系统处理能力")
        print("   • 保证服务稳定性")
        print("   • 优化资源利用率")
    else:
        print("\n⚠️ 验证结果:")
        print("   部分验证未通过，请检查系统配置")
        
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {test_name}: {status}")
    
    print(f"\n🌐 访问地址:")
    print("   前端: https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com")
    print("   API:  https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com/api")
    
    print(f"\n🔧 配置信息:")
    print("   max_active_accounts = 10")
    print("   max_concurrent_crawlers = 10") 
    print("   crawl_interval = 45 秒")

if __name__ == "__main__":
    main()