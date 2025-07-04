from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timedelta
import random
import platform
import io
import logging
import time
import re
import os
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from collections import defaultdict

app = FastAPI(title="小八爬虫管理系统", description="师门登录优化版 v2.5 - 自动化增强版")
api_router = APIRouter(prefix="/api")

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 全局数据存储
accounts_db = []
memory_data = []
keyword_stats = defaultdict(int)
crawl_history = []
auto_crawl_running = False
accumulated_data = {}

# 默认关键词监控列表
DEFAULT_MONITOR_KEYWORDS = [
    "人脸提示", "没钱了", "网络异常", "登录失败", "验证码", 
    "账号冻结", "系统维护", "连接超时", "服务器错误", "掉线"
]

# 动态关键词监控列表（可以增删）
MONITOR_KEYWORDS = DEFAULT_MONITOR_KEYWORDS.copy()

class CrawlerAccount(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password: str
    status: str = "inactive"  # inactive, active, running, paused, error
    preferred_guild: Optional[str] = None
    last_crawl: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_auto_enabled: bool = True
    crawl_count: int = 0
    success_rate: float = 0.0
    last_error: Optional[str] = None

class CrawlerAccountCreate(BaseModel):
    username: str
    password: str
    preferred_guild: Optional[str] = None

class CrawlerAccountUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    preferred_guild: Optional[str] = None
    is_auto_enabled: Optional[bool] = None
    status: Optional[str] = None

class CrawlerData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account_username: str
    sequence_number: int
    ip: str
    type: str
    name: str
    level: int
    guild: str
    skill: str
    count_current: int
    count_total: int
    total_time: str
    status: str
    runtime: str
    crawl_timestamp: datetime = Field(default_factory=datetime.utcnow)
    accumulated_count: int = 0
    cycle_count: int = 0

class CrawlerConfig(BaseModel):
    target_url: str = "http://xiao8.lodsve.com:6007/x8login"
    crawl_interval: int = 45
    headless: bool = True
    timeout: int = 30
    auto_crawl_enabled: bool = False
    max_concurrent_crawlers: int = 10
    max_active_accounts: int = 10

class KeywordRequest(BaseModel):
    keyword: str

class KeywordListRequest(BaseModel):
    keywords: List[str]

class FilterRequest(BaseModel):
    account_username: Optional[str] = None
    guild: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    min_level: Optional[int] = None
    max_level: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    keyword: Optional[str] = None

class BatchOperationRequest(BaseModel):
    account_ids: List[str]
    operation: str  # start, stop, pause, resume, delete

# 优化的师门登录爬虫类
class OptimizedGuildCrawler:
    def __init__(self, account: CrawlerAccount, config: CrawlerConfig):
        self.account = account
        self.config = config
        self.driver = None
        self.last_data = {}
        
    def setup_driver(self):
        """设置浏览器驱动"""
        try:
            chrome_options = Options()
            if self.config.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 使用系统安装的chromium浏览器
            chrome_options.binary_location = "/usr/bin/chromium"
            
            # 尝试使用系统chromium驱动或自动下载适配版本
            try:
                # 首先尝试使用系统的chromium驱动
                service = Service("/usr/bin/chromedriver") if os.path.exists("/usr/bin/chromedriver") else Service()
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception:
                # 如果失败，尝试自动下载适配的驱动
                try:
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                except Exception:
                    # 最后尝试直接启动chromium
                    self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.set_page_load_timeout(self.config.timeout)
            
            # 移除webdriver检测
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info(f"浏览器驱动设置完成: {self.account.username}")
            return True
        except Exception as e:
            logger.error(f"浏览器驱动设置失败: {str(e)}")
            return False
    
    def precise_guild_login(self):
        """精确的师门登录流程 - 基于实际页面结构优化"""
        try:
            logger.info(f"开始师门登录: {self.account.username}")
            
            # 1. 访问登录页面
            self.driver.get(self.config.target_url)
            
            # 等待页面加载完成 - 等待输入框和按钮出现
            WebDriverWait(self.driver, 15).until(
                lambda driver: len(driver.find_elements(By.TAG_NAME, "input")) >= 2 and
                               len(driver.find_elements(By.TAG_NAME, "button")) >= 1
            )
            
            logger.info("登录页面加载完成")
            time.sleep(2)  # 确保页面完全渲染
            
            # 2. 确保师门选项被选中
            try:
                select_element = self.driver.find_element(By.NAME, "sprite_type")
                if select_element.get_attribute("value") != "sm":
                    select_element.send_keys("sm")
                logger.info("✅ 师门选项确认选中")
            except Exception as e:
                logger.warning(f"师门选项设置警告: {e}")
            
            # 3. 填写用户名和密码
            logger.info("开始填写登录信息...")
            
            # 填写用户名
            try:
                username_field = self.driver.find_element(By.NAME, "Username")
                username_field.clear()
                username_field.send_keys(self.account.username)
                logger.info(f"✅ 用户名填写完成: {self.account.username}")
            except Exception:
                logger.error("❌ 未找到用户名输入框")
                return False
            
            # 填写密码
            try:
                password_field = self.driver.find_element(By.NAME, "Password")
                password_field.clear()
                password_field.send_keys(self.account.password)
                logger.info("✅ 密码填写完成")
            except Exception:
                logger.error("❌ 未找到密码输入框")
                return False
            
            time.sleep(1)
            
            # 4. 点击登录按钮
            logger.info("查找并点击登录按钮...")
            
            try:
                login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                login_button.click()
                logger.info("✅ 登录按钮点击成功")
            except Exception:
                try:
                    login_button = self.driver.find_element(By.CLASS_NAME, "btn")
                    login_button.click()
                    logger.info("✅ 通过class找到登录按钮并点击")
                except Exception:
                    logger.error("❌ 未找到登录按钮")
                    return False
            
            # 5. 等待登录完成
            logger.info("等待登录完成...")
            
            try:
                # 等待页面跳转或URL变化
                WebDriverWait(self.driver, 25).until(
                    lambda driver: (
                        driver.current_url != self.config.target_url or 
                        "后台管理" not in driver.page_source or
                        len(driver.find_elements(By.XPATH, "//input[@type='password']")) == 0
                    )
                )
                
                current_url = self.driver.current_url
                page_title = self.driver.title
                
                logger.info(f"✅ 师门登录成功: {self.account.username}")
                logger.info(f"🎯 当前URL: {current_url}")
                logger.info(f"🎯 页面标题: {page_title}")
                
                time.sleep(2)  # 等待页面稳定
                return True
                
            except TimeoutException:
                logger.error(f"❌ 师门登录超时: {self.account.username}")
                
                # 检查是否有错误提示
                try:
                    page_text = self.driver.page_source
                    if any(keyword in page_text for keyword in ['错误', '失败', '用户名或密码', 'error']):
                        logger.error("🚨 登录失败，可能是账号密码错误")
                    else:
                        logger.error("🚨 登录超时，页面无响应")
                except:
                    pass
                
                return False
                
        except Exception as e:
            logger.error(f"❌ 师门登录过程异常: {self.account.username}, 错误: {str(e)}")
            return False
    
    def extract_guild_data(self):
        """提取师门监控数据"""
        try:
            logger.info("开始提取师门数据...")
            
            # 等待数据表格加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            tables = soup.find_all('table')
            data_list = []
            
            for table in tables:
                rows = table.find_all('tr')
                for i, row in enumerate(rows[1:], 1):  # 跳过表头
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 8:
                        try:
                            # 解析次数/总次数
                            count_text = cols[7].get_text(strip=True) if len(cols) > 7 else "0/0"
                            count_match = re.match(r'(\d+)/(\d+)', count_text)
                            count_current = int(count_match.group(1)) if count_match else 0
                            count_total = int(count_match.group(2)) if count_match else 0
                            
                            # 检查关键词
                            status_text = cols[9].get_text(strip=True) if len(cols) > 9 else ""
                            self.check_keywords(status_text)
                            
                            # 数据累计逻辑
                            accumulated_count, cycle_count = self.calculate_accumulated_data(
                                self.account.username, i, count_current, count_total
                            )
                            
                            data_item = CrawlerData(
                                account_username=self.account.username,
                                sequence_number=i,
                                ip=cols[1].get_text(strip=True) if len(cols) > 1 else "",
                                type=cols[2].get_text(strip=True) if len(cols) > 2 else "",
                                name=cols[3].get_text(strip=True) if len(cols) > 3 else "",
                                level=int(cols[4].get_text(strip=True)) if len(cols) > 4 and cols[4].get_text(strip=True).isdigit() else 0,
                                guild=cols[5].get_text(strip=True) if len(cols) > 5 else "",
                                skill=cols[6].get_text(strip=True) if len(cols) > 6 else "",
                                count_current=count_current,
                                count_total=count_total,
                                total_time=cols[8].get_text(strip=True) if len(cols) > 8 else "",
                                status=status_text,
                                runtime=cols[10].get_text(strip=True) if len(cols) > 10 else "",
                                accumulated_count=accumulated_count,
                                cycle_count=cycle_count
                            )
                            data_list.append(data_item)
                        except Exception as e:
                            logger.warning(f"解析数据行失败: {str(e)}")
                            continue
            
            logger.info(f"成功提取 {len(data_list)} 条师门数据")
            return data_list
            
        except Exception as e:
            logger.error(f"提取师门数据失败: {str(e)}")
            return []
    
    def check_keywords(self, text):
        """检查关键词并统计"""
        global keyword_stats
        for keyword in MONITOR_KEYWORDS:
            if keyword in text:
                keyword_stats[keyword] += 1
                logger.warning(f"发现关键词: {keyword} 在文本: {text}")
    
    def calculate_accumulated_data(self, username, seq_num, current_count, total_count):
        """计算累计数据逻辑"""
        global accumulated_data
        
        key = f"{username}_{seq_num}"
        
        if key not in accumulated_data:
            accumulated_data[key] = {
                "last_count": current_count,
                "accumulated": 0,
                "cycles": 0
            }
        
        last_data = accumulated_data[key]
        
        # 检测重置（从高数值跳到低数值，如 11/199 → 1/199）
        if current_count < last_data["last_count"] and last_data["last_count"] > total_count * 0.05:
            last_data["accumulated"] += last_data["last_count"]
            last_data["cycles"] += 1
            logger.info(f"数据重置检测: {username} seq{seq_num} 从 {last_data['last_count']} 重置到 {current_count}")
        
        last_data["last_count"] = current_count
        
        return last_data["accumulated"] + current_count, last_data["cycles"]
    
    def save_data(self, data_list):
        """保存数据到内存"""
        global memory_data, crawl_history
        
        # 保存历史记录
        crawl_history.append({
            "timestamp": datetime.utcnow(),
            "account": self.account.username,
            "success": len(data_list) > 0,
            "data_count": len(data_list)
        })
        
        # 更新主数据
        for data_item in data_list:
            # 检查是否已存在相同记录
            existing_index = -1
            for i, existing in enumerate(memory_data):
                if (existing["account_username"] == data_item.account_username and
                    existing["sequence_number"] == data_item.sequence_number and
                    existing["ip"] == data_item.ip):
                    existing_index = i
                    break
            
            if existing_index >= 0:
                memory_data[existing_index] = data_item.dict()
            else:
                memory_data.append(data_item.dict())
        
        logger.info(f"保存师门数据: {len(data_list)} 条记录")
    
    def run_guild_crawl(self):
        """完整的师门爬取流程"""
        try:
            if not self.setup_driver():
                return False
            
            # 执行师门登录
            if not self.precise_guild_login():
                return False
            
            # 提取师门数据
            data_list = self.extract_guild_data()
            
            if data_list:
                self.save_data(data_list)
                logger.info(f"师门爬取完成: {self.account.username}, 获取 {len(data_list)} 条数据")
                return True
            else:
                logger.warning(f"未获取到师门数据: {self.account.username}")
                return False
                
        except Exception as e:
            logger.error(f"师门爬取失败: {self.account.username}, 错误: {str(e)}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

# 自动爬虫任务
async def auto_crawl_task():
    """45秒自动爬虫任务 - 保持10个账号活跃"""
    global auto_crawl_running, accounts_db
    
    logger.info("启动自动爬虫任务 - 维持10个账号活跃模式...")
    
    while auto_crawl_running:
        try:
            # 获取配置
            config = CrawlerConfig()
            max_active = config.max_active_accounts
            
            # 确保有足够的账号
            if len(accounts_db) < max_active:
                logger.info(f"账号数量不足，当前{len(accounts_db)}个，需要{max_active}个")
                await asyncio.sleep(45)
                continue
            
            # 强制将前max_active个账号设置为活跃状态
            for i, acc in enumerate(accounts_db[:max_active]):
                if acc.get("status") not in ["running"]:  # 只有正在运行的不改变状态
                    acc["status"] = "active"
                    acc["is_auto_enabled"] = True
            
            # 将超出限制的账号设置为非活跃
            for acc in accounts_db[max_active:]:
                acc["status"] = "inactive"
                acc["is_auto_enabled"] = False
            
            # 获取活跃账号进行爬取
            active_accounts = [acc for acc in accounts_db[:max_active] if acc.get("is_auto_enabled", True)]
            
            if not active_accounts:
                logger.info("没有可用的活跃账号")
                await asyncio.sleep(45)
                continue
            
            logger.info(f"开始45秒爬虫周期，维持 {len(active_accounts)} 个活跃账号...")
            
            # 分批执行爬虫任务
            max_concurrent = min(config.max_concurrent_crawlers, len(active_accounts))
            
            for i in range(0, len(active_accounts), max_concurrent):
                batch = active_accounts[i:i + max_concurrent]
                tasks = []
                
                for acc_data in batch:
                    # 更新账号状态为运行中
                    for acc in accounts_db:
                        if acc["id"] == acc_data["id"]:
                            acc["status"] = "running"
                            acc["last_crawl"] = datetime.utcnow()
                            break
                    
                    # 创建爬虫任务
                    account = CrawlerAccount(**acc_data)
                    crawler = OptimizedGuildCrawler(account, config)
                    tasks.append(asyncio.create_task(asyncio.to_thread(crawler.run_guild_crawl)))
                
                # 等待这批任务完成
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 更新账号状态和统计，强制保持活跃
                for j, result in enumerate(results):
                    acc_data = batch[j]
                    for acc in accounts_db:
                        if acc["id"] == acc_data["id"]:
                            acc["crawl_count"] = acc.get("crawl_count", 0) + 1
                            if isinstance(result, Exception):
                                # 即使出错也保持活跃状态，只记录错误
                                acc["status"] = "active"  # 强制保持活跃
                                acc["last_error"] = str(result)
                                acc["success_rate"] = max(0.1, acc.get("success_rate", 0.5))  # 最低保持10%
                                logger.warning(f"账号 {acc['username']} 爬取出错，但保持活跃: {str(result)}")
                            elif result:
                                acc["status"] = "active"  # 成功后保持活跃
                                acc["last_error"] = None
                                acc["success_rate"] = min(1.0, acc.get("success_rate", 0.5) + 0.1)
                                logger.info(f"账号 {acc['username']} 爬取成功")
                            else:
                                # 即使失败也保持活跃状态
                                acc["status"] = "active"  # 强制保持活跃
                                acc["success_rate"] = max(0.1, acc.get("success_rate", 0.5))  # 最低保持10%
                                logger.warning(f"账号 {acc['username']} 爬取失败，但保持活跃")
                            
                            # 确保自动启用标志始终为True（仅前max_active个）
                            acc["is_auto_enabled"] = True
                            break
                
                logger.info(f"完成一批爬虫任务: {len(batch)} 个账号")
                
                # 如果还有更多批次，等待一小段时间
                if i + max_concurrent < len(active_accounts):
                    await asyncio.sleep(5)
            
            # 统计当前活跃账号数
            current_active = len([acc for acc in accounts_db if acc.get("status") in ["active", "running"]])
            logger.info(f"自动爬虫周期完成，当前活跃账号: {current_active}/{max_active}，等待 {config.crawl_interval} 秒...")
            await asyncio.sleep(config.crawl_interval)
            
        except Exception as e:
            logger.error(f"自动爬虫任务异常: {str(e)}")
            # 即使出现异常也要保持前max_active个账号活跃
            for i, acc in enumerate(accounts_db[:config.max_active_accounts]):
                acc["status"] = "active"
                acc["is_auto_enabled"] = True
            await asyncio.sleep(45)

# API路由
@api_router.get("/")
async def root():
    return {
        "message": "小八爬虫管理系统 - 师门登录优化版", 
        "version": "2.5",
        "architecture": platform.machine(),
        "update": "2025-01-08 自动化增强版",
        "features": ["45秒自动爬虫", "多账号管理", "数据累计", "关键词统计", "数据筛选"]
    }

@api_router.get("/version")
async def get_version():
    return {
        "version": "2.5",
        "update_date": "2025-01-08",
        "features": ["45秒自动爬虫", "多账号管理", "数据累计逻辑", "关键词统计", "数据筛选", "增强CSV导出"],
        "architecture": platform.machine(),
        "changelog": [
            "✅ 实现45秒自动爬虫持续运行",
            "✅ 添加完整的多账号管理系统",
            "✅ 实现数据累计逻辑（重置检测）",
            "✅ 增加关键词监控和统计",
            "✅ 实现数据筛选和分析功能",
            "✅ 增强CSV导出功能"
        ]
    }

# 自动爬虫控制
@api_router.post("/crawler/auto/start")
async def start_auto_crawler(background_tasks: BackgroundTasks):
    global auto_crawl_running
    if not auto_crawl_running:
        auto_crawl_running = True
        background_tasks.add_task(auto_crawl_task)
        return {"message": "自动爬虫启动成功", "interval": "45秒", "version": "2.5"}
    return {"message": "自动爬虫已在运行中"}

@api_router.post("/crawler/auto/stop")
async def stop_auto_crawler():
    global auto_crawl_running
    auto_crawl_running = False
    return {"message": "自动爬虫停止成功"}

@api_router.get("/crawler/config")
async def get_crawler_config():
    """获取爬虫配置信息"""
    config = CrawlerConfig()
    return {
        "target_url": config.target_url,
        "crawl_interval": config.crawl_interval,
        "headless": config.headless,
        "timeout": config.timeout,
        "max_concurrent_crawlers": config.max_concurrent_crawlers,
        "max_active_accounts": config.max_active_accounts,
        "auto_crawl_enabled": auto_crawl_running,
        "version": "2.5"
    }

@api_router.get("/crawler/auto/status")
async def get_auto_crawler_status():
    return {
        "running": auto_crawl_running,
        "interval": 45,
        "total_accounts": len(accounts_db),
        "active_accounts": len([acc for acc in accounts_db if acc.get("is_auto_enabled", True)]),
        "crawl_history_count": len(crawl_history)
    }

# 账号管理
@api_router.post("/accounts", response_model=CrawlerAccount)
async def create_account(account: CrawlerAccountCreate):
    # 检查用户名是否已存在
    for acc in accounts_db:
        if acc["username"] == account.username:
            raise HTTPException(status_code=400, detail="用户名已存在")
    
    new_account = CrawlerAccount(**account.dict())
    accounts_db.append(new_account.dict())
    return new_account

@api_router.get("/accounts")
async def get_accounts():
    return accounts_db

@api_router.get("/accounts/{account_id}")
async def get_account(account_id: str):
    for acc in accounts_db:
        if acc["id"] == account_id:
            return acc
    raise HTTPException(status_code=404, detail="账号不存在")

@api_router.put("/accounts/{account_id}")
async def update_account(account_id: str, account_update: CrawlerAccountUpdate):
    for i, acc in enumerate(accounts_db):
        if acc["id"] == account_id:
            update_data = account_update.dict(exclude_unset=True)
            accounts_db[i].update(update_data)
            return accounts_db[i]
    raise HTTPException(status_code=404, detail="账号不存在")

@api_router.delete("/accounts/{account_id}")
async def delete_account(account_id: str):
    for i, acc in enumerate(accounts_db):
        if acc["id"] == account_id:
            deleted_account = accounts_db.pop(i)
            return {"message": "账号删除成功", "account": deleted_account}
    raise HTTPException(status_code=404, detail="账号不存在")

@api_router.post("/accounts/batch")
async def batch_operation(request: BatchOperationRequest):
    """批量操作账号"""
    affected_accounts = []
    
    for account_id in request.account_ids:
        for acc in accounts_db:
            if acc["id"] == account_id:
                if request.operation == "start":
                    acc["is_auto_enabled"] = True
                    acc["status"] = "active"
                elif request.operation == "stop":
                    acc["is_auto_enabled"] = False
                    acc["status"] = "inactive"
                elif request.operation == "pause":
                    acc["status"] = "paused"
                elif request.operation == "resume":
                    acc["status"] = "active"
                elif request.operation == "delete":
                    accounts_db.remove(acc)
                
                affected_accounts.append(acc)
                break
    
    return {
        "message": f"批量{request.operation}操作完成",
        "affected_count": len(affected_accounts),
        "accounts": affected_accounts
    }

# 数据管理和筛选
@api_router.get("/crawler/data")
async def get_data():
    return memory_data

@api_router.post("/crawler/data/filter")
async def filter_data(filter_req: FilterRequest):
    """数据筛选"""
    filtered_data = memory_data.copy()
    
    if filter_req.account_username:
        filtered_data = [d for d in filtered_data if d["account_username"] == filter_req.account_username]
    
    if filter_req.guild:
        filtered_data = [d for d in filtered_data if filter_req.guild in d["guild"]]
    
    if filter_req.type:
        filtered_data = [d for d in filtered_data if filter_req.type in d["type"]]
    
    if filter_req.status:
        filtered_data = [d for d in filtered_data if filter_req.status in d["status"]]
    
    if filter_req.min_level:
        filtered_data = [d for d in filtered_data if d["level"] >= filter_req.min_level]
    
    if filter_req.max_level:
        filtered_data = [d for d in filtered_data if d["level"] <= filter_req.max_level]
    
    if filter_req.keyword:
        filtered_data = [d for d in filtered_data if 
                        filter_req.keyword.lower() in d["name"].lower() or
                        filter_req.keyword.lower() in d["status"].lower()]
    
    if filter_req.start_date:
        start_date = datetime.fromisoformat(filter_req.start_date.replace('Z', '+00:00'))
        filtered_data = [d for d in filtered_data if 
                        datetime.fromisoformat(d["crawl_timestamp"].replace('Z', '+00:00')) >= start_date]
    
    if filter_req.end_date:
        end_date = datetime.fromisoformat(filter_req.end_date.replace('Z', '+00:00'))
        filtered_data = [d for d in filtered_data if 
                        datetime.fromisoformat(d["crawl_timestamp"].replace('Z', '+00:00')) <= end_date]
    
    return {
        "total_count": len(memory_data),
        "filtered_count": len(filtered_data),
        "data": filtered_data
    }

# 统计分析
@api_router.get("/crawler/stats")
async def get_statistics():
    """获取统计分析数据"""
    if not memory_data:
        return {"message": "暂无数据"}
    
    # 基础统计
    total_records = len(memory_data)
    unique_accounts = len(set(d["account_username"] for d in memory_data))
    unique_guilds = len(set(d["guild"] for d in memory_data if d["guild"]))
    unique_types = len(set(d["type"] for d in memory_data if d["type"]))
    
    # 等级统计
    levels = [d["level"] for d in memory_data if d["level"] > 0]
    avg_level = sum(levels) / len(levels) if levels else 0
    max_level = max(levels) if levels else 0
    min_level = min(levels) if levels else 0
    
    # 账号统计
    account_stats = defaultdict(int)
    for d in memory_data:
        account_stats[d["account_username"]] += 1
    
    # 门派统计
    guild_stats = defaultdict(int)
    for d in memory_data:
        if d["guild"]:
            guild_stats[d["guild"]] += 1
    
    # 类型统计
    type_stats = defaultdict(int)
    for d in memory_data:
        if d["type"]:
            type_stats[d["type"]] += 1
    
    # 累计数据统计
    total_accumulated = sum(d.get("accumulated_count", 0) for d in memory_data)
    total_cycles = sum(d.get("cycle_count", 0) for d in memory_data)
    
    return {
        "basic_stats": {
            "total_records": total_records,
            "unique_accounts": unique_accounts,
            "unique_guilds": unique_guilds,
            "unique_types": unique_types,
            "avg_level": round(avg_level, 2),
            "max_level": max_level,
            "min_level": min_level
        },
        "account_distribution": dict(account_stats),
        "guild_distribution": dict(guild_stats),
        "type_distribution": dict(type_stats),
        "accumulation_stats": {
            "total_accumulated_count": total_accumulated,
            "total_cycles": total_cycles,
            "avg_accumulated_per_record": round(total_accumulated / total_records, 2) if total_records > 0 else 0
        }
    }

# 关键词统计
@api_router.get("/crawler/keywords")
async def get_keyword_stats():
    """获取关键词统计"""
    return {
        "keyword_stats": dict(keyword_stats),
        "total_keywords_detected": sum(keyword_stats.values()),
        "unique_keywords": len(keyword_stats),
        "monitored_keywords": MONITOR_KEYWORDS,
        "default_keywords": DEFAULT_MONITOR_KEYWORDS
    }

@api_router.post("/crawler/keywords/reset")
async def reset_keyword_stats():
    """重置关键词统计"""
    global keyword_stats
    keyword_stats.clear()
    return {"message": "关键词统计已重置"}

@api_router.post("/crawler/keywords/add")
async def add_custom_keyword(request: KeywordRequest):
    """添加自定义关键词"""
    global MONITOR_KEYWORDS
    
    keyword = request.keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="关键词不能为空")
    
    if keyword in MONITOR_KEYWORDS:
        raise HTTPException(status_code=400, detail="关键词已存在")
    
    MONITOR_KEYWORDS.append(keyword)
    logger.info(f"添加自定义关键词: {keyword}")
    
    return {
        "message": f"关键词 '{keyword}' 添加成功",
        "keyword": keyword,
        "total_keywords": len(MONITOR_KEYWORDS),
        "monitored_keywords": MONITOR_KEYWORDS
    }

@api_router.delete("/crawler/keywords/{keyword}")
async def delete_keyword(keyword: str):
    """删除关键词"""
    global MONITOR_KEYWORDS
    
    if keyword not in MONITOR_KEYWORDS:
        raise HTTPException(status_code=404, detail="关键词不存在")
    
    if keyword in DEFAULT_MONITOR_KEYWORDS:
        raise HTTPException(status_code=400, detail="默认关键词不能删除")
    
    MONITOR_KEYWORDS.remove(keyword)
    
    # 同时清除该关键词的统计数据
    if keyword in keyword_stats:
        del keyword_stats[keyword]
    
    logger.info(f"删除关键词: {keyword}")
    
    return {
        "message": f"关键词 '{keyword}' 删除成功",
        "keyword": keyword,
        "total_keywords": len(MONITOR_KEYWORDS),
        "monitored_keywords": MONITOR_KEYWORDS
    }

@api_router.post("/crawler/keywords/batch")
async def batch_add_keywords(request: KeywordListRequest):
    """批量添加关键词"""
    global MONITOR_KEYWORDS
    
    added_keywords = []
    skipped_keywords = []
    
    for keyword in request.keywords:
        keyword = keyword.strip()
        if not keyword:
            continue
            
        if keyword in MONITOR_KEYWORDS:
            skipped_keywords.append(keyword)
        else:
            MONITOR_KEYWORDS.append(keyword)
            added_keywords.append(keyword)
    
    logger.info(f"批量添加关键词: {added_keywords}")
    
    return {
        "message": f"批量添加完成",
        "added_keywords": added_keywords,
        "skipped_keywords": skipped_keywords,
        "added_count": len(added_keywords),
        "skipped_count": len(skipped_keywords),
        "total_keywords": len(MONITOR_KEYWORDS),
        "monitored_keywords": MONITOR_KEYWORDS
    }

@api_router.get("/crawler/keywords/defaults")
async def get_default_keywords():
    """获取默认关键词列表"""
    return {
        "default_keywords": DEFAULT_MONITOR_KEYWORDS,
        "current_keywords": MONITOR_KEYWORDS,
        "custom_keywords": [k for k in MONITOR_KEYWORDS if k not in DEFAULT_MONITOR_KEYWORDS]
    }

@api_router.post("/crawler/keywords/restore-defaults")
async def restore_default_keywords():
    """恢复默认关键词"""
    global MONITOR_KEYWORDS
    
    # 保留自定义关键词
    custom_keywords = [k for k in MONITOR_KEYWORDS if k not in DEFAULT_MONITOR_KEYWORDS]
    
    # 重置为默认关键词 + 自定义关键词
    MONITOR_KEYWORDS = DEFAULT_MONITOR_KEYWORDS.copy() + custom_keywords
    
    logger.info("恢复默认关键词设置")
    
    return {
        "message": "默认关键词已恢复",
        "default_keywords": DEFAULT_MONITOR_KEYWORDS,
        "custom_keywords": custom_keywords,
        "total_keywords": len(MONITOR_KEYWORDS),
        "monitored_keywords": MONITOR_KEYWORDS
    }

# 爬虫历史
@api_router.get("/crawler/history")
async def get_crawl_history():
    """获取爬虫历史记录"""
    return {
        "history": crawl_history[-100:],  # 最近100条记录
        "total_crawls": len(crawl_history),
        "success_rate": len([h for h in crawl_history if h["success"]]) / len(crawl_history) if crawl_history else 0
    }

# 原有API保持兼容
@api_router.post("/crawler/start")
async def start_crawler():
    global accounts_db
    config = CrawlerConfig()
    max_active = config.max_active_accounts
    
    if len(accounts_db) < max_active:
        # 创建足够的账号以达到max_active数量
        base_accounts = ["KR666", "KR777", "KR888", "KR999", "KR000"]
        additional_accounts = ["KR001", "KR002", "KR003", "KR004", "KR005"]
        
        all_usernames = base_accounts + additional_accounts
        
        # 清空现有账号并重新创建
        accounts_db.clear()
        
        for i in range(max_active):
            username = all_usernames[i] if i < len(all_usernames) else f"KR{str(i+1).zfill(3)}"
            account = CrawlerAccount(
                username=username, 
                password="69203532xX",
                status="active" if i < max_active else "inactive",
                is_auto_enabled=i < max_active
            )
            accounts_db.append(account.dict())
    
    # 确保前max_active个账号为活跃状态
    for i, acc in enumerate(accounts_db):
        if i < max_active:
            acc["status"] = "active"
            acc["is_auto_enabled"] = True
        else:
            acc["status"] = "inactive"
            acc["is_auto_enabled"] = False
    
    active_count = len([acc for acc in accounts_db if acc.get("is_auto_enabled", False)])
    
    return {
        "message": "师门爬虫启动成功", 
        "accounts": len(accounts_db), 
        "active_accounts": active_count,
        "max_active_accounts": max_active,
        "version": "2.5"
    }

@api_router.post("/crawler/mock-data")
async def generate_mock_data():
    memory_data.clear()
    for account in ["KR666", "KR777", "KR888", "KR999", "KR000"]:
        for i in range(5):
            data = CrawlerData(
                account_username=account,
                sequence_number=i + 1,
                ip=f"222.210.79.{115 + i}",
                type=random.choice(["鬼砍", "剑客", "杀手", "跑商"]),
                name=f"师门角色{i+1}",
                level=random.randint(80, 120),
                guild=random.choice(["青帮", "无门派", "九雷剑", "五毒", "天龙寺", "普陀山", "方寸山"]),
                skill=str(random.randint(0, 3)),
                count_current=random.randint(1, 50),
                count_total=random.randint(100, 200),
                total_time=f"{random.randint(1, 12)}/199",
                status=random.choice(["在线", "离线", "修炼中", "跑商中", "没钱了"]),
                runtime=f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00",
                accumulated_count=random.randint(0, 500),
                cycle_count=random.randint(0, 5)
            )
            memory_data.append(data.dict())
    return {"message": f"生成了 {len(memory_data)} 条师门演示数据（v2.5增强版）"}

@api_router.post("/crawler/test/{username}")
async def test_optimized_guild_login(username: str):
    """测试优化后的师门登录"""
    try:
        account_data = None
        for acc in accounts_db:
            if acc["username"] == username:
                account_data = acc
                break
        
        if not account_data:
            return {"test_result": "failed", "message": "账号不存在"}
        
        account = CrawlerAccount(**account_data)
        config = CrawlerConfig()
        
        crawler = OptimizedGuildCrawler(account, config)
        
        # 执行完整的师门爬取流程
        success = crawler.run_guild_crawl()
        
        if success:
            message = f"师门登录优化版测试成功！已提取数据到系统"
            result = "success"
        else:
            message = "师门登录优化版测试失败，请检查日志"
            result = "failed"
        
        return {
            "username": username,
            "test_result": result,
            "message": message,
            "version": "2.5",
            "login_type": "师门登录优化版"
        }
        
    except Exception as e:
        return {
            "test_result": "failed", 
            "message": f"测试出错: {str(e)}",
            "version": "2.5"
        }

@api_router.get("/crawler/status")
async def get_status():
    active_accounts = len([acc for acc in accounts_db if acc.get("status") == "active"])
    return {
        "total_accounts": len(accounts_db),
        "active_accounts": active_accounts,
        "total_records": len(memory_data),
        "crawl_status": "running" if auto_crawl_running else "stopped",
        "system_info": f"师门登录优化版 v2.5 - {platform.machine()}",
        "version": "2.5",
        "last_update": "2025-01-08",
        "auto_crawl_running": auto_crawl_running,
        "keyword_alerts": sum(keyword_stats.values())
    }

@api_router.get("/crawler/data/export")
async def export_csv():
    """增强的CSV导出功能"""
    if not memory_data:
        df = pd.DataFrame(columns=["账号", "序号", "IP", "类型", "命名", "等级", "门派", "绝技", "当前次数", "总次数", "累计次数", "周期数", "总时间", "状态", "运行时间", "抓取时间"])
    else:
        df = pd.DataFrame([{
            "账号": item["account_username"],
            "序号": item["sequence_number"],
            "IP": item["ip"],
            "类型": item["type"],
            "命名": item["name"],
            "等级": item["level"],
            "门派": item["guild"],
            "绝技": item["skill"],
            "当前次数": item["count_current"],
            "总次数": item["count_total"],
            "累计次数": item.get("accumulated_count", 0),
            "周期数": item.get("cycle_count", 0),
            "总时间": item["total_time"],
            "状态": item["status"],
            "运行时间": item["runtime"],
            "抓取时间": item["crawl_timestamp"]
        } for item in memory_data])
    
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=guild_crawler_v2.5_enhanced.csv"}
    )

app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])