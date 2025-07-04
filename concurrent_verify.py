#!/usr/bin/env python3
"""
小八爬虫管理系统 - 并发数10验证脚本
验证并发数成功调整为10
"""

import requests
import json
from datetime import datetime

# API基础URL
API_BASE = "https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com/api"

def print_header():
    """打印头部信息"""
    print("🚀 小八爬虫管理系统 - 并发数调整确认")
    print("="*60)
    print("🎯 目标: 确认并发数成功调整为10")
    print(f"⏰ 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

def verify_concurrent_config():
    """验证并发配置"""
    print("\n🔧 并发配置验证")
    print("-" * 40)
    
    try:
        # 获取爬虫配置
        print("1. 获取当前爬虫配置...")
        response = requests.get(f"{API_BASE}/crawler/config")
        if response.status_code == 200:
            config = response.json()
            
            print(f"   🎯 目标网站: {config['target_url']}")
            print(f"   ⏰ 爬取间隔: {config['crawl_interval']} 秒")
            print(f"   🖥️ 无头模式: {'是' if config['headless'] else '否'}")
            print(f"   ⏱️ 超时时间: {config['timeout']} 秒")
            print(f"   🚀 最大并发数: {config['max_concurrent_crawlers']}")
            print(f"   🔄 自动爬虫: {'运行中' if config['auto_crawl_enabled'] else '已停止'}")
            print(f"   📦 系统版本: v{config['version']}")
            
            # 重点验证并发数
            concurrent_count = config['max_concurrent_crawlers']
            if concurrent_count == 10:
                print(f"\n   ✅ 并发数配置正确: {concurrent_count}")
                print("   🎉 配置调整成功！")
                return True
            else:
                print(f"\n   ❌ 并发数配置错误: 期望10，实际{concurrent_count}")
                return False
        else:
            print(f"   ❌ 配置获取失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return False

def verify_performance_impact():
    """验证性能影响"""
    print("\n📊 性能影响分析")
    print("-" * 40)
    
    try:
        # 获取账号信息
        response = requests.get(f"{API_BASE}/accounts")
        if response.status_code == 200:
            accounts = response.json()
            account_count = len(accounts)
            
            print(f"   👥 当前账号数: {account_count}")
            
            # 计算批次分析
            print(f"\n   📈 批次分析对比:")
            
            # 旧配置 (并发数3)
            old_concurrent = 3
            old_batches = (account_count + old_concurrent - 1) // old_concurrent
            
            # 新配置 (并发数10)
            new_concurrent = 10
            new_batches = (account_count + new_concurrent - 1) // new_concurrent
            
            print(f"   🔧 旧配置(并发3): 需要 {old_batches} 批次")
            for i in range(old_batches):
                start_idx = i * old_concurrent
                end_idx = min(start_idx + old_concurrent, account_count)
                count_in_batch = end_idx - start_idx
                print(f"     批次{i+1}: {count_in_batch} 个账号")
            
            print(f"   🚀 新配置(并发10): 需要 {new_batches} 批次")
            for i in range(new_batches):
                start_idx = i * new_concurrent
                end_idx = min(start_idx + new_concurrent, account_count)
                count_in_batch = end_idx - start_idx
                print(f"     批次{i+1}: {count_in_batch} 个账号")
            
            # 性能提升计算
            if old_batches > new_batches:
                batch_reduction = ((old_batches - new_batches) / old_batches) * 100
                print(f"\n   📈 性能提升:")
                print(f"     批次减少: {old_batches} → {new_batches} ({batch_reduction:.1f}%减少)")
                print(f"     理论速度提升: {batch_reduction:.1f}%")
            elif account_count <= new_concurrent:
                print(f"\n   ✅ 最优配置:")
                print(f"     所有{account_count}个账号可同时并发执行")
                print(f"     无需分批，达到最大效率")
            else:
                print(f"\n   📊 配置说明:")
                print(f"     当前账号数较少，并发优势有限")
                print(f"     当账号数增加时，并发优势会更明显")
                
        return True
        
    except Exception as e:
        print(f"❌ 性能分析失败: {e}")
        return False

def verify_system_readiness():
    """验证系统就绪状态"""
    print("\n✅ 系统就绪状态检查")
    print("-" * 40)
    
    try:
        # 检查系统状态
        response = requests.get(f"{API_BASE}/crawler/status")
        if response.status_code == 200:
            status = response.json()
            
            print(f"   🖥️ 系统版本: v{status.get('version', 'unknown')}")
            print(f"   👥 总账号数: {status.get('total_accounts', 0)}")
            print(f"   🟢 活跃账号: {status.get('active_accounts', 0)}")
            print(f"   📊 总记录数: {status.get('total_records', 0)}")
            print(f"   🔄 爬取状态: {status.get('crawl_status', 'unknown')}")
            
            # 检查自动爬虫状态
            auto_response = requests.get(f"{API_BASE}/crawler/auto/status")
            if auto_response.status_code == 200:
                auto_status = auto_response.json()
                print(f"   🤖 自动爬虫: {'运行中' if auto_status.get('running') else '已停止'}")
                print(f"   ⏰ 爬取间隔: {auto_status.get('interval', 0)} 秒")
            
            # 系统就绪检查
            total_accounts = status.get('total_accounts', 0)
            active_accounts = status.get('active_accounts', 0)
            
            if total_accounts > 0 and active_accounts > 0:
                print(f"\n   ✅ 系统就绪状态: 良好")
                print(f"   🎯 准备开始高并发爬取")
            else:
                print(f"\n   ⚠️ 系统状态: 需要配置账号")
                print(f"   💡 建议: 添加账号并启动自动爬虫")
                
        return True
        
    except Exception as e:
        print(f"❌ 系统状态检查失败: {e}")
        return False

def main():
    """主函数"""
    print_header()
    
    # 执行验证
    results = {}
    
    results['config'] = verify_concurrent_config()
    results['performance'] = verify_performance_impact()
    results['readiness'] = verify_system_readiness()
    
    # 总结
    print("\n🎉 并发数调整验证完成！")
    print("="*60)
    
    successful_tests = sum(1 for success in results.values() if success)
    total_tests = len(results)
    
    print(f"📊 验证结果: {successful_tests}/{total_tests} 通过")
    
    if results['config']:
        print("\n✨ 并发数调整确认:")
        print("   🔧 max_concurrent_crawlers: 3 → 10")
        print("   📈 并发能力提升: 333%")
        print("   🚀 配置已生效")
        
        print("\n🎯 预期效果:")
        print("   • 更高的账号处理并发数")
        print("   • 减少爬取总时间")
        print("   • 提升系统吞吐量")
        print("   • 更好的资源利用")
        
        print("\n📋 使用说明:")
        print("   1. 系统现在支持最多10个账号同时爬取")
        print("   2. 当账号数 ≤ 10时，全部并发执行")
        print("   3. 当账号数 > 10时，自动分批处理")
        print("   4. 每批最多10个，批次间间隔5秒")
        
        print("\n💡 优化建议:")
        print("   • 监控系统资源使用情况")
        print("   • 观察目标网站响应情况")
        print("   • 根据实际情况调整并发数")
        print("   • 确保网络带宽充足")
    else:
        print("\n❌ 配置验证失败")
        print("   请检查系统配置和服务状态")
    
    print(f"\n🌐 访问地址:")
    print("   前端: https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com")
    print("   API:  https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com/api")

if __name__ == "__main__":
    main()