from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
import random
import platform
import io
import logging
import time
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

app = FastAPI(title="小八爬虫管理系统", description="师门登录优化版 v2.1")
api_router = APIRouter(prefix="/api")

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 内存存储
accounts_db = []
memory_data = []

class CrawlerAccount(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password: str
    status: str = "inactive"
    preferred_guild: Optional[str] = None
    last_crawl: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CrawlerAccountCreate(BaseModel):
    username: str
    password: str
    preferred_guild: Optional[str] = None

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

class CrawlerConfig(BaseModel):
    target_url: str = "http://xiao8.lodsve.com:6007/x8login"
    crawl_interval: int = 50
    headless: bool = True
    timeout: int = 30

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
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
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
            
            # 2. 点击师门按钮 - 基于实际页面结构
            guild_clicked = False
            
            # 策略1: 通过文本"师门"查找按钮
            try:
                guild_button = self.driver.find_element(By.XPATH, "//button[text()='师门']")
                if guild_button.is_displayed() and guild_button.is_enabled():
                    guild_button.click()
                    logger.info("✅ 通过文本找到师门按钮并点击")
                    guild_clicked = True
            except NoSuchElementException:
                pass
            
            # 策略2: 通过包含"师门"文本查找
            if not guild_clicked:
                try:
                    guild_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '师门')]")
                    if guild_button.is_displayed() and guild_button.is_enabled():
                        guild_button.click()
                        logger.info("✅ 通过包含文本找到师门按钮并点击")
                        guild_clicked = True
                except NoSuchElementException:
                    pass
            
            # 策略3: 查找input类型的师门按钮
            if not guild_clicked:
                try:
                    guild_input = self.driver.find_element(By.XPATH, "//input[@value='师门']")
                    if guild_input.is_displayed() and guild_input.is_enabled():
                        guild_input.click()
                        logger.info("✅ 找到师门input按钮并点击")
                        guild_clicked = True
                except NoSuchElementException:
                    pass
            
            # 策略4: 根据页面结构，假设第一个蓝色按钮是师门
            if not guild_clicked:
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    visible_buttons = [btn for btn in buttons if btn.is_displayed() and btn.is_enabled()]
                    
                    if len(visible_buttons) >= 1:
                        visible_buttons[0].click()
                        logger.info("✅ 点击第一个可见按钮（推测为师门）")
                        guild_clicked = True
                except Exception as e:
                    logger.warning(f"按钮策略失败: {e}")
            
            if guild_clicked:
                time.sleep(1)  # 等待师门选择生效
                logger.info("师门按钮点击完成")
            else:
                logger.warning("⚠️ 未找到师门按钮，继续登录流程")
            
            # 3. 填写用户名和密码
            logger.info("开始填写登录信息...")
            
            # 查找所有输入框
            input_fields = self.driver.find_elements(By.TAG_NAME, "input")
            text_inputs = [inp for inp in input_fields 
                          if inp.get_attribute('type') in ['text', 'email', 'tel', None] 
                          and inp.is_displayed()]
            password_inputs = [inp for inp in input_fields 
                             if inp.get_attribute('type') == 'password' 
                             and inp.is_displayed()]
            
            logger.info(f"找到 {len(text_inputs)} 个文本输入框，{len(password_inputs)} 个密码输入框")
            
            # 填写用户名
            if text_inputs:
                username_field = text_inputs[0]
                username_field.clear()
                username_field.send_keys(self.account.username)
                logger.info(f"✅ 用户名填写完成: {self.account.username}")
            else:
                logger.error("❌ 未找到用户名输入框")
                return False
            
            # 填写密码
            if password_inputs:
                password_field = password_inputs[0]
                password_field.clear()
                password_field.send_keys(self.account.password)
                logger.info("✅ 密码填写完成")
            else:
                logger.error("❌ 未找到密码输入框")
                return False
            
            time.sleep(1)
            
            # 4. 点击登录按钮
            logger.info("查找并点击登录按钮...")
            
            login_clicked = False
            
            # 策略1: 通过文本"登录"查找
            try:
                login_button = self.driver.find_element(By.XPATH, "//button[text()='登录']")
                if login_button.is_displayed() and login_button.is_enabled():
                    login_button.click()
                    logger.info("✅ 通过文本找到登录按钮并点击")
                    login_clicked = True
            except NoSuchElementException:
                pass
            
            # 策略2: 通过包含"登录"文本查找
            if not login_clicked:
                try:
                    login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '登录')]")
                    if login_button.is_displayed() and login_button.is_enabled():
                        login_button.click()
                        logger.info("✅ 通过包含文本找到登录按钮并点击")
                        login_clicked = True
                except NoSuchElementException:
                    pass
            
            # 策略3: 查找input类型的登录按钮
            if not login_clicked:
                try:
                    login_input = self.driver.find_element(By.XPATH, "//input[@value='登录']")
                    if login_input.is_displayed() and login_input.is_enabled():
                        login_input.click()
                        logger.info("✅ 找到登录input按钮并点击")
                        login_clicked = True
                except NoSuchElementException:
                    pass
            
            # 策略4: 查找submit类型按钮
            if not login_clicked:
                try:
                    submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                        "input[type='submit'], button[type='submit']")
                    for btn in submit_buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            btn.click()
                            logger.info("✅ 找到submit按钮并点击")
                            login_clicked = True
                            break
                except Exception:
                    pass
            
            # 策略5: 假设第二个按钮是登录（如果有两个按钮）
            if not login_clicked:
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    visible_buttons = [btn for btn in buttons if btn.is_displayed() and btn.is_enabled()]
                    
                    if len(visible_buttons) >= 2:
                        visible_buttons[1].click()
                        logger.info("✅ 点击第二个可见按钮（推测为登录）")
                        login_clicked = True
                    elif len(visible_buttons) == 1:
                        visible_buttons[0].click()
                        logger.info("✅ 点击唯一可见按钮（推测为登录）")
                        login_clicked = True
                except Exception as e:
                    logger.warning(f"按钮策略登录失败: {e}")
            
            if not login_clicked:
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
                                status=cols[9].get_text(strip=True) if len(cols) > 9 else "",
                                runtime=cols[10].get_text(strip=True) if len(cols) > 10 else ""
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
    
    def save_data(self, data_list):
        """保存数据到内存"""
        global memory_data
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

# API路由
@api_router.get("/")
async def root():
    return {
        "message": "小八爬虫管理系统 - 师门登录优化版", 
        "version": "2.1",
        "architecture": platform.machine(),
        "update": "2025-01-08 师门登录流程优化"
    }

@api_router.get("/version")
async def get_version():
    return {
        "version": "2.1",
        "update_date": "2025-01-08",
        "features": ["精确师门登录", "多策略按钮识别", "增强错误处理", "页面结构优化"],
        "architecture": platform.machine(),
        "changelog": [
            "✅ 基于实际页面结构优化师门按钮识别",
            "✅ 增加多种按钮查找策略",
            "✅ 优化页面加载等待逻辑", 
            "✅ 增强登录流程错误处理",
            "✅ 提升师门登录成功率"
        ]
    }

@api_router.post("/crawler/start")
async def start_crawler():
    if not accounts_db:
        default_accounts = ["KR666", "KR777", "KR888", "KR999", "KR000"]
        for username in default_accounts:
            account = CrawlerAccount(username=username, password="69203532xX")
            accounts_db.append(account.dict())
    return {"message": "师门爬虫启动成功", "accounts": len(accounts_db), "version": "2.1"}

@api_router.get("/crawler/accounts")
async def get_accounts():
    return accounts_db

@api_router.get("/crawler/data")
async def get_data():
    return memory_data

@api_router.post("/crawler/mock-data")
async def generate_mock_data():
    memory_data.clear()
    for account in ["KR666", "KR777", "KR888", "KR999", "KR000"]:
        for i in range(5):
            data = CrawlerData(
                account_username=account,
                sequence_number=i + 1,
                ip=f"222.210.79.{115 + i}",
                type=random.choice(["鬼砍", "剑客", "杀手"]),
                name=f"师门角色{i+1}",
                level=random.randint(80, 120),
                guild=random.choice(["青帮", "无门派", "九雷剑", "五毒", "天龙寺"]),
                skill=str(random.randint(0, 3)),
                count_current=random.randint(1, 50),
                count_total=random.randint(100, 200),
                total_time=f"{random.randint(1, 12)}/199",
                status=random.choice(["在线", "离线", "修炼中"]),
                runtime=f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00"
            )
            memory_data.append(data.dict())
    return {"message": f"生成了 {len(memory_data)} 条师门演示数据（v2.1优化版）"}

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
            "version": "2.1",
            "login_type": "师门登录优化版"
        }
        
    except Exception as e:
        return {
            "test_result": "failed", 
            "message": f"测试出错: {str(e)}",
            "version": "2.1"
        }

@api_router.get("/crawler/status")
async def get_status():
    return {
        "total_accounts": len(accounts_db),
        "active_accounts": 0,
        "total_records": len(memory_data),
        "crawl_status": "stopped",
        "system_info": f"师门登录优化版 v2.1 - {platform.machine()}",
        "version": "2.1",
        "last_update": "2025-01-08"
    }

@api_router.get("/crawler/data/export")
async def export_csv():
    if not memory_data:
        df = pd.DataFrame(columns=["账号", "序号", "IP", "类型", "命名", "等级", "门派", "次数", "状态"])
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
            "次数": f"{item['count_current']}/{item['count_total']}",
            "总时间": item["total_time"],
            "状态": item["status"],
            "运行时间": item["runtime"]
        } for item in memory_data])
    
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=guild_crawler_v2.1.csv"}
    )

app.include_router(api_router)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])