import time
import random
import json
import os
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from configparser import ConfigParser

class AutoFollow:
    def __init__(self, id, pwd, keywords, account_follow_limit):
        self.id = id
        self.pwd = pwd
        self.keywords = keywords
        self.account_follow_limit = account_follow_limit

        if os.path.exists("send_follow_account.json"):
            with open("send_follow_account.json", "r") as f:
                self.send_follow_account_dict = json.load(f)
        else:
            self.send_follow_account_dict = {} 
        self.send_follow_account = self.send_follow_account_dict.get(self.id, [])

        self.driver = webdriver.Chrome(options = self.set_chrome_options())     

    def set_chrome_options(self):
        # chromedriver_autoinstaller.install(cwd=True)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.page_load_strategy = 'eager'
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        # chrome_options.add_argument("--headless")

        return chrome_options
    
    def login(self):
        self.driver.set_window_size(780, 450)
        self.driver.get("https://www.instagram.com/accounts/login/")
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.NAME, "username")))
        self.driver.find_element(By.NAME, "username").send_keys(self.id)
        time.sleep(0.5)
        self.driver.find_element(By.NAME, "password").send_keys(self.pwd)
        time.sleep(0.5)
        self.driver.find_element(By.NAME, "password").send_keys(Keys.ENTER)

        self.handle_pop_up()
    
    def handle_pop_up(self):
        WebDriverWait(self.driver, 45).until(EC.presence_of_element_located((By.XPATH, "//div[text()='稍後再說']")))
        self.driver.find_element(By.XPATH, "//div[text()='稍後再說']").click()
        # WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, "//button[@class='_a9-- _a9_1']")))
        # self.driver.find_element(By.XPATH, "//button[@class='_a9-- _a9_1']").click()
    
    def get_fan_account_url(self, keyword):
        WebDriverWait(self.driver, 45).until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='搜尋輸入']")))
        self.driver.find_element(By.XPATH, "//input[@aria-label='搜尋輸入']").send_keys(keyword) 
        # //div[@class='x9f619 x78zum5 xdt5ytf x1iyjqo2 x6ikm8r x1odjw0f xocp1fn']/a # //div[@role='none']/a 
        time.sleep(5)
        fan_account = self.driver.find_elements(By.XPATH, "//div[@role='none']/a")
        if not fan_account:
            fan_account = self.driver.find_elements(By.XPATH, "//div[@class='x9f619 x78zum5 xdt5ytf x1iyjqo2 x6ikm8r x1odjw0f xocp1fn']/a")
        self.fan_account_url = [i.get_attribute("href") for i in fan_account if "/explore/" not in i.get_attribute("href")]

    def follow(self, keyword_follow_limit):
        send_folllow = 0
        stop = False
        for url in self.fan_account_url:
            if stop:
                break

            self.driver.get(url)
            WebDriverWait(self.driver, 45).until(EC.presence_of_element_located((By.XPATH, "//ul[@class='x78zum5 x1q0g3np xieb3on']/li[2]/a")))
            self.driver.find_element(By.XPATH, "//ul[@class='x78zum5 x1q0g3np xieb3on']/li[2]/a").click()
            WebDriverWait(self.driver, 45).until(EC.presence_of_element_located((By.CLASS_NAME, "_aano")))

            modal = self.driver.find_element(By.CLASS_NAME, "_aano")
            WebDriverWait(self.driver, 45).until(EC.presence_of_element_located((By.XPATH, "//div[@class='_aano']/div[1]/div/div/div/div/div/div[3]/div/button")))
            for i in range(5):
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
                time.sleep(random.uniform(2.0, 5.0))

            accounts = self.driver.find_elements(By.XPATH, "//div[@class='_aano']/div[1]/div/div")
            same_fan_account_follow = 0
            for i in accounts:
                if send_folllow < keyword_follow_limit:
                    if same_fan_account_follow < self.account_follow_limit:
                        try:
                            button = i.find_element(By.XPATH, ".//div/div/div/div[3]/div/button")
                        except:
                            continue
                        if button.is_enabled() and button.find_element(By.XPATH, ".//div/div").text == "追蹤":
                            button.click()
                            self.send_follow_account.append(i.find_element(By.XPATH, ".//div/div/div/div[1]//a").get_attribute("href"))
                            same_fan_account_follow += 1
                            send_folllow += 1
                            time.sleep(random.uniform(1.0, 3.0))
                        else:
                            time.sleep(0.2)
                    else:
                        break
                else:
                    stop = True
                    break

            self.send_follow_account_dict[self.id] = self.send_follow_account
            with open("send_follow_account.json", "w") as f:
                json.dump(self.send_follow_account_dict, f, indent = 4)

        print(f"follow status: {send_folllow}/{keyword_follow_limit}")
        print("==========================")

    def run(self):
        self.login()
        for keyword, keyword_follow_limit in self.keywords.items():
            print("==========================")
            print(f"keyword: {keyword}")
            self.get_fan_account_url(keyword)
            self.follow(keyword_follow_limit)
            self.driver.get("https://www.instagram.com/")
        self.driver.quit()

if __name__ == "__main__":
    cfg = ConfigParser()
    cfg.read("cfg.ini", encoding="utf-8")
    ID = cfg["ig_login_information"]["id"]
    PWD = cfg["ig_login_information"]["password"]
    KEYWORDS = {}
    for k in cfg["condition"]["keywords"].split():
        key, value = k.split(":")
        KEYWORDS[key] = int(value)
    ACCOUNT_FOLLOW_LIMIT = int(cfg["condition"]["account_follow_limit"])
    bot = AutoFollow(ID, PWD, KEYWORDS, ACCOUNT_FOLLOW_LIMIT)
    bot.run()