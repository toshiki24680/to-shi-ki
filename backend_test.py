import requests
import sys
import time
from datetime import datetime

class XiaoBaCrawlerTester:
    def __init__(self, base_url="https://ffaa6b35-d505-4ab9-9968-ab9ba881d29f.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.account_id = None  # Store created account ID for later tests

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if response.headers.get('content-type') and 'application/json' in response.headers.get('content-type'):
                    print(f"Response: {response.json()}")
                elif response.headers.get('content-type') and 'text/csv' in response.headers.get('content-type'):
                    print(f"CSV data received, length: {len(response.content)} bytes")
                else:
                    print(f"Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")

            return success, response

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, None

    def test_root_endpoint(self):
        """Test the root endpoint"""
        success, response = self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )
        if success:
            data = response.json()
            if data.get('version') == "2.5":
                print("✅ Version information correct: 2.5")
            else:
                print(f"❌ Version information incorrect: {data.get('version')}")
        return success

    def test_version_endpoint(self):
        """Test the version endpoint"""
        success, response = self.run_test(
            "Version Endpoint",
            "GET",
            "version",
            200
        )
        if success:
            data = response.json()
            if data.get('version') == "2.5":
                print("✅ Version information correct: 2.5")
            else:
                print(f"❌ Version information incorrect: {data.get('version')}")
            
            # Check for new features
            features = data.get('features', [])
            expected_features = ["45秒自动爬虫", "多账号管理", "数据累计逻辑", "关键词统计", "数据筛选", "增强CSV导出"]
            for feature in expected_features:
                if feature in features:
                    print(f"✅ Feature found: {feature}")
                else:
                    print(f"❌ Feature missing: {feature}")
        return success

    def test_start_crawler(self):
        """Test starting the crawler"""
        success, response = self.run_test(
            "Start Crawler",
            "POST",
            "crawler/start",
            200
        )
        return success

    def test_get_accounts(self):
        """Test getting accounts"""
        success, response = self.run_test(
            "Get Accounts",
            "GET",
            "accounts",
            200
        )
        if success:
            accounts = response.json()
            print(f"Found {len(accounts)} accounts")
        return success
        
    def test_create_account(self):
        """Test creating a new account"""
        test_account = {
            "username": "KR666",
            "password": "69203532xX",
            "preferred_guild": "青帮"
        }
        
        success, response = self.run_test(
            "Create Account",
            "POST",
            "accounts",
            200,
            data=test_account
        )
        
        if success and response.json().get('id'):
            self.account_id = response.json().get('id')
            print(f"✅ Account created with ID: {self.account_id}")
        elif response and response.status_code == 400:
            # Account might already exist, try to get it
            success2, accounts_response = self.run_test(
                "Get Accounts to Find Existing",
                "GET",
                "accounts",
                200
            )
            if success2:
                accounts = accounts_response.json()
                for account in accounts:
                    if account.get("username") == "KR666":
                        self.account_id = account.get("id")
                        print(f"✅ Found existing account with ID: {self.account_id}")
                        return True
        return success
        
    def test_update_account(self):
        """Test updating an account"""
        if not self.account_id:
            print("❌ Cannot test account update - no account ID available")
            self.tests_run += 1  # Count as run but not passed
            return False
            
        update_data = {
            "is_auto_enabled": False,
            "status": "paused"
        }
        
        try:
            url = f"{self.api_url}/accounts/{self.account_id}"
            headers = {'Content-Type': 'application/json'}
            
            self.tests_run += 1
            print(f"\n🔍 Testing Update Account...")
            
            response = requests.put(url, json=update_data, headers=headers)
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                print(f"Response: {response.json()}")
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                print(f"Response: {response.text}")
            
            return success
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False
        
    def test_auto_crawler_control(self):
        """Test auto crawler control"""
        # Start auto crawler
        success1, response1 = self.run_test(
            "Start Auto Crawler",
            "POST",
            "crawler/auto/start",
            200
        )
        
        # Check auto crawler status
        success2, response2 = self.run_test(
            "Get Auto Crawler Status",
            "GET",
            "crawler/auto/status",
            200
        )
        
        if success2:
            status = response2.json()
            if status.get('running'):
                print("✅ Auto crawler is running")
            else:
                print("❌ Auto crawler is not running")
        
        # Stop auto crawler
        success3, response3 = self.run_test(
            "Stop Auto Crawler",
            "POST",
            "crawler/auto/stop",
            200
        )
        
        # Verify it's stopped
        success4, response4 = self.run_test(
            "Verify Auto Crawler Stopped",
            "GET",
            "crawler/auto/status",
            200
        )
        
        if success4:
            status = response4.json()
            if not status.get('running'):
                print("✅ Auto crawler is stopped")
            else:
                print("❌ Auto crawler is still running")
        
        return success1 and success2 and success3 and success4
        
    def test_data_filtering(self):
        """Test data filtering functionality"""
        # First ensure we have some data
        self.test_start_crawler()
        time.sleep(2)  # Give the server a moment to process
        
        # Test filtering by account
        filter_data = {
            "account_username": "KR666",
            "min_level": 80
        }
        
        success, response = self.run_test(
            "Filter Data by Account and Level",
            "POST",
            "crawler/data/filter",
            200,
            data=filter_data
        )
        
        if success:
            data = response.json()
            print(f"Filtered data count: {data.get('filtered_count')}")
            print(f"Total data count: {data.get('total_count')}")
        
        return success
        
    def test_statistics(self):
        """Test statistics functionality"""
        success, response = self.run_test(
            "Get Statistics",
            "GET",
            "crawler/stats",
            200
        )
        
        if success:
            stats = response.json()
            print(f"Basic stats: {stats.get('basic_stats')}")
            print(f"Accumulation stats: {stats.get('accumulation_stats')}")
        
        return success
        
    def test_keyword_stats(self):
        """Test keyword statistics functionality"""
        success1, response1 = self.run_test(
            "Get Keyword Stats",
            "GET",
            "crawler/keywords",
            200
        )
        
        if success1:
            stats = response1.json()
            print(f"Total keywords detected: {stats.get('total_keywords_detected')}")
            print(f"Monitored keywords: {stats.get('monitored_keywords')}")
        
        # Test resetting keyword stats
        success2, response2 = self.run_test(
            "Reset Keyword Stats",
            "POST",
            "crawler/keywords/reset",
            200
        )
        
        return success1 and success2
        
    def test_crawl_history(self):
        """Test crawl history functionality"""
        success, response = self.run_test(
            "Get Crawl History",
            "GET",
            "crawler/history",
            200
        )
        
        if success:
            history = response.json()
            print(f"Total crawls: {history.get('total_crawls')}")
            print(f"Success rate: {history.get('success_rate')}")
        
        return success
        
    def test_batch_operation(self):
        """Test batch operation on accounts"""
        # Use real accounts for testing
        real_accounts = [
            {"username": "KR777", "password": "69203532xX", "preferred_guild": "无门派"},
            {"username": "KR888", "password": "69203532xX", "preferred_guild": "天龙寺"},
            {"username": "KR999", "password": "69203532xX", "preferred_guild": "方寸山"}
        ]
        
        account_ids = []
        for i, account_data in enumerate(real_accounts):
            success, response = self.run_test(
                f"Create Real Test Account {i+1}",
                "POST",
                "accounts",
                200,
                data=account_data
            )
            
            if success and response.json().get('id'):
                account_ids.append(response.json().get('id'))
            elif response and response.status_code == 400:
                # Account might already exist, try to get it
                success2, accounts_response = self.run_test(
                    "Get Accounts to Find Existing",
                    "GET",
                    "accounts",
                    200
                )
                if success2:
                    accounts = accounts_response.json()
                    for account in accounts:
                        if account.get("username") == account_data["username"]:
                            account_ids.append(account.get("id"))
                            print(f"✅ Found existing account with ID: {account.get('id')}")
        
        if not account_ids:
            print("❌ Cannot test batch operations - no accounts available")
            return False
            
        # Test batch start operation
        batch_data = {
            "account_ids": account_ids,
            "operation": "start"
        }
        
        success, response = self.run_test(
            "Batch Start Operation",
            "POST",
            "accounts/batch",
            200,
            data=batch_data
        )
        
        # Test batch stop operation
        batch_data["operation"] = "stop"
        success2, response2 = self.run_test(
            "Batch Stop Operation",
            "POST",
            "accounts/batch",
            200,
            data=batch_data
        )
        
        # Don't delete the real accounts
        return success and success2

    def test_get_data(self):
        """Test getting crawler data"""
        success, response = self.run_test(
            "Get Crawler Data",
            "GET",
            "crawler/data",
            200
        )
        if success:
            data = response.json()
            print(f"Found {len(data)} data records")
        return success

    def test_generate_mock_data(self):
        """Test generating mock data"""
        success, response = self.run_test(
            "Generate Mock Data",
            "POST",
            "crawler/mock-data",
            200
        )
        return success

    def test_get_status(self):
        """Test getting crawler status"""
        success, response = self.run_test(
            "Get Crawler Status",
            "GET",
            "crawler/status",
            200
        )
        if success:
            status = response.json()
            print(f"System version: {status.get('version')}")
            print(f"Total accounts: {status.get('total_accounts')}")
            print(f"Total records: {status.get('total_records')}")
        return success

    def test_export_csv(self):
        """Test exporting data as CSV"""
        success, response = self.run_test(
            "Export CSV",
            "GET",
            "crawler/data/export",
            200
        )
        return success
    
    def test_optimized_login(self, username="KR666"):
        """Test optimized login for a specific account"""
        success, response = self.run_test(
            f"Test Optimized Login for {username}",
            "POST",
            f"crawler/test/{username}",
            200
        )
        if success:
            result = response.json()
            print(f"Login test result: {result.get('test_result')}")
            print(f"Message: {result.get('message')}")
        return success

def main():
    # Setup
    tester = XiaoBaCrawlerTester()
    
    # Run tests
    print("=" * 50)
    print("🚀 Testing 小八爬虫管理系统 API - 师门登录优化版 v2.5")
    print("=" * 50)
    
    # Test basic endpoints
    tester.test_root_endpoint()
    tester.test_version_endpoint()
    
    # Test account management
    tester.test_create_account()
    tester.test_get_accounts()
    tester.test_update_account()
    tester.test_batch_operation()
    
    # Test auto crawler functionality
    tester.test_auto_crawler_control()
    
    # Test crawler functionality
    tester.test_start_crawler()
    time.sleep(2)  # Give the server a moment to process
    tester.test_get_data()
    
    # Test data filtering and statistics
    tester.test_data_filtering()
    tester.test_statistics()
    tester.test_keyword_stats()
    tester.test_crawl_history()
    
    # Test status and export
    tester.test_get_status()
    tester.test_export_csv()
    
    # Test optimized login with real account
    tester.test_optimized_login("KR666")
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print("=" * 50)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())