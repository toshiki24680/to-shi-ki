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
            if data.get('version') == "2.1":
                print("✅ Version information correct: 2.1")
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
            if data.get('version') == "2.1":
                print("✅ Version information correct: 2.1")
            else:
                print(f"❌ Version information incorrect: {data.get('version')}")
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
            "crawler/accounts",
            200
        )
        if success:
            accounts = response.json()
            print(f"Found {len(accounts)} accounts")
        return success

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
    print("🚀 Testing 小八爬虫管理系统 API - 师门登录优化版 v2.1")
    print("=" * 50)
    
    # Test basic endpoints
    tester.test_root_endpoint()
    tester.test_version_endpoint()
    
    # Test crawler functionality
    tester.test_start_crawler()
    tester.test_get_accounts()
    
    # Test data generation and retrieval
    tester.test_generate_mock_data()
    time.sleep(1)  # Give the server a moment to process
    tester.test_get_data()
    
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