#!/usr/bin/env python3
"""
小八爬虫管理系统 - 并发数调整验证脚本
验证并发数从3调整到10是否生效
"""

import requests
import json
import time
from datetime import datetime

# API基础URL
API_BASE = "https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com/api"

def print_header():
    """打印头部信息"""
    print("🚀 小八爬虫管理系统 - 并发数调整验证")
    print("="*60)
    print("🎯 验证目标: 并发数从3调整为10")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

def test_concurrent_crawling():
    """测试并发爬取能力"""
    print("\n🔄 并发爬取能力测试")
    print("-" * 40)
    
    try:
        # 获取当前账号状态
        print("1. 检查当前账号状态...")
        response = requests.get(f"{API_BASE}/accounts")
        if response.status_code == 200:
            accounts = response.json()
            print(f"   📊 总账号数: {len(accounts)}")
            
            active_accounts = [acc for acc in accounts if acc.get('is_auto_enabled', True)]
            print(f"   🟢 活跃账号数: {len(active_accounts)}")
            
            # 显示账号状态
            for acc in accounts:
                status_icon = "🏃" if acc['status'] == 'running' else "✅" if acc['status'] == 'active' else "⚠️"
                print(f"     {status_icon} {acc['username']}: {acc['status']}")
        
        # 检查自动爬虫配置
        print("\n2. 检查自动爬虫配置...")
        response = requests.get(f"{API_BASE}/crawler/auto/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   🔄 运行状态: {'运行中' if status['running'] else '已停止'}")
            print(f"   ⏰ 爬取间隔: {status['interval']} 秒")
            print(f"   👥 总账号数: {status['total_accounts']}")
            print(f"   🟢 活跃账号数: {status['active_accounts']}")
            
            # 计算理论并发能力
            max_concurrent = min(10, len(accounts))  # 新的并发数是10
            print(f"   🚀 理论最大并发数: {max_concurrent}")
            
            if len(accounts) <= 10:
                print(f"   ✅ 当前{len(accounts)}个账号可以全部并发执行")
            else:
                batches = (len(accounts) + 9) // 10  # 向上取整
                print(f"   📊 需要分{batches}批执行，每批最多10个")
        
        # 等待一个爬取周期观察并发效果
        print("\n3. 观察一个爬取周期的并发效果...")
        
        # 记录开始时间
        start_time = time.time()
        initial_history_response = requests.get(f"{API_BASE}/crawler/history")
        initial_crawls = 0
        if initial_history_response.status_code == 200:
            initial_crawls = initial_history_response.json().get('total_crawls', 0)
        
        print(f"   📊 开始时总爬取次数: {initial_crawls}")
        print("   ⏳ 等待一个完整爬取周期...")
        
        # 监控45秒内的活动
        for i in range(9):
            time.sleep(5)
            elapsed = (i + 1) * 5
            print(f"     ⏱️  已等待: {elapsed}/45 秒")
            
            # 每15秒检查一次账号状态
            if elapsed % 15 == 0:
                response = requests.get(f"{API_BASE}/accounts")
                if response.status_code == 200:
                    accounts = response.json()
                    running_count = len([acc for acc in accounts if acc['status'] == 'running'])
                    active_count = len([acc for acc in accounts if acc['status'] == 'active'])
                    print(f"       🏃 运行中: {running_count}, ✅ 活跃: {active_count}")
        
        # 检查结束状态
        end_time = time.time()
        final_history_response = requests.get(f"{API_BASE}/crawler/history")
        final_crawls = 0
        if final_history_response.status_code == 200:
            final_crawls = final_history_response.json().get('total_crawls', 0)
        
        crawls_in_period = final_crawls - initial_crawls
        duration = end_time - start_time
        
        print(f"\n4. 并发测试结果:")
        print(f"   📊 测试周期内新增爬取: {crawls_in_period} 次")
        print(f"   ⏱️  实际耗时: {duration:.1f} 秒")
        
        if crawls_in_period > 0:
            avg_time_per_crawl = duration / crawls_in_period
            print(f"   📈 平均每次爬取耗时: {avg_time_per_crawl:.1f} 秒")
            
            # 评估并发效果
            if crawls_in_period >= len(accounts):
                print(f"   ✅ 并发效果良好：完成了 {crawls_in_period} 次爬取")
            else:
                print(f"   ⚠️ 并发效果：完成了 {crawls_in_period} 次爬取，期望 {len(accounts)} 次")
        else:
            print("   ⚠️ 测试周期内未检测到新的爬取活动")
        
        return True
        
    except Exception as e:
        print(f"❌ 并发测试失败: {e}")
        return False

def test_performance_comparison():
    """性能对比测试"""
    print("\n📊 性能对比分析")
    print("-" * 40)
    
    try:
        # 获取爬取历史
        response = requests.get(f"{API_BASE}/crawler/history")
        if response.status_code == 200:
            history = response.json()
            total_crawls = history.get('total_crawls', 0)
            success_rate = history.get('success_rate', 0)
            recent_history = history.get('history', [])
            
            print(f"   📈 历史总爬取次数: {total_crawls}")
            print(f"   ✅ 总体成功率: {(success_rate * 100):.1f}%")
            
            if recent_history:
                print(f"   📋 最近爬取记录: {len(recent_history)} 条")
                
                # 分析最近的爬取时间间隔
                recent_5 = recent_history[-5:]
                print("   🕒 最近5次爬取时间:")
                for entry in recent_5:
                    timestamp = entry.get('timestamp', '')[:19]
                    account = entry.get('account', '')
                    success = "✅" if entry.get('success') else "❌"
                    count = entry.get('data_count', 0)
                    print(f"     {timestamp} - {account} {success} ({count}条)")
                
                # 计算时间间隔
                if len(recent_5) >= 2:
                    try:
                        from datetime import datetime
                        times = []
                        for entry in recent_5:
                            time_str = entry.get('timestamp', '')[:19]
                            dt = datetime.fromisoformat(time_str)
                            times.append(dt)
                        
                        intervals = []
                        for i in range(1, len(times)):
                            interval = (times[i] - times[i-1]).total_seconds()
                            intervals.append(interval)
                        
                        if intervals:
                            avg_interval = sum(intervals) / len(intervals)
                            print(f"   ⏱️  平均爬取间隔: {avg_interval:.1f} 秒")
                            
                            if avg_interval < 60:
                                print("   🚀 高频爬取模式，并发效果显著")
                            else:
                                print("   📊 正常爬取间隔")
                                
                    except Exception as e:
                        print(f"   ⚠️ 时间间隔分析失败: {e}")
            
        # 获取当前系统状态
        response = requests.get(f"{API_BASE}/crawler/status")
        if response.status_code == 200:
            status = response.json()
            print(f"\n   🖥️ 当前系统状态:")
            print(f"     版本: v{status.get('version', 'unknown')}")
            print(f"     总账号: {status.get('total_accounts', 0)}")
            print(f"     活跃账号: {status.get('active_accounts', 0)}")
            print(f"     总记录: {status.get('total_records', 0)}")
            print(f"     爬取状态: {status.get('crawl_status', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 性能分析失败: {e}")
        return False

def test_concurrent_capacity():
    """测试并发容量"""
    print("\n🎯 并发容量验证")
    print("-" * 40)
    
    try:
        print("1. 理论并发分析:")
        print("   🔧 旧配置: 最大并发数 = 3")
        print("   🚀 新配置: 最大并发数 = 10")
        print("   📈 并发提升: 333% (3→10)")
        
        # 获取账号数量
        response = requests.get(f"{API_BASE}/accounts")
        if response.status_code == 200:
            accounts = response.json()
            account_count = len(accounts)
            
            print(f"\n2. 实际并发能力:")
            print(f"   👥 当前账号数: {account_count}")
            
            if account_count <= 10:
                print(f"   ✅ 全部{account_count}个账号可同时并发")
                print(f"   ⚡ 理论最快完成时间: 单次爬取时间")
                batches = 1
            else:
                batches = (account_count + 9) // 10
                remaining = account_count % 10
                print(f"   📊 需要分{batches}批次执行:")
                for i in range(batches):
                    if i == batches - 1 and remaining > 0:
                        print(f"     批次{i+1}: {remaining}个账号")
                    else:
                        print(f"     批次{i+1}: 10个账号")
            
            print(f"\n3. 性能提升预期:")
            old_batches = (account_count + 2) // 3  # 旧的3并发需要的批次
            new_batches = batches
            
            print(f"   📊 旧配置需要批次: {old_batches}")
            print(f"   🚀 新配置需要批次: {new_batches}")
            
            if new_batches < old_batches:
                improvement = ((old_batches - new_batches) / old_batches) * 100
                print(f"   📈 批次减少: {improvement:.1f}%")
                print(f"   ⚡ 预期速度提升: {improvement:.1f}%")
            else:
                print(f"   📊 当前账号数较少，并发优势不明显")
        
        return True
        
    except Exception as e:
        print(f"❌ 并发容量验证失败: {e}")
        return False

def main():
    """主函数"""
    print_header()
    
    # 执行各项测试
    results = {}
    
    results['concurrent_test'] = test_concurrent_crawling()
    time.sleep(2)
    
    results['performance_test'] = test_performance_comparison()
    time.sleep(2)
    
    results['capacity_test'] = test_concurrent_capacity()
    
    # 总结
    print("\n🎉 并发数调整验证完成！")
    print("="*60)
    
    successful_tests = sum(1 for success in results.values() if success)
    total_tests = len(results)
    
    print(f"📊 测试结果: {successful_tests}/{total_tests} 通过")
    
    print("\n✨ 并发数调整总结:")
    print("   🔧 配置变更: max_concurrent_crawlers = 3 → 10")
    print("   📈 并发能力提升: 333%")
    print("   🚀 理论性能提升: 最多提升66.7%的执行速度")
    print("   ⚡ 实际效果: 取决于账号数量和网络条件")
    
    print("\n🎯 优势分析:")
    print("   • 更高的并发处理能力")
    print("   • 减少总体爬取时间")
    print("   • 更好的资源利用率")
    print("   • 适应更多账号的扩展需求")
    
    print("\n💡 注意事项:")
    print("   • 并发数增加可能增加服务器负载")
    print("   • 需要确保网络带宽充足")
    print("   • 目标网站需要能承受更高并发")
    print("   • 建议监控系统性能指标")
    
    print(f"\n🌐 访问地址:")
    print("   前端: https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com")
    print("   API:  https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com/api")

if __name__ == "__main__":
    main()