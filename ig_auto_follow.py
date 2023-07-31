import time
import random
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from configparser import ConfigParser

class AutoFollow:
    def __init__(self, id, pwd, keyword, total_follow_limit, account_follow_limit):
        self.id = id
        self.pwd = pwd
        self.keyword = keyword
        self.total_follow_limit = total_follow_limit
        self.account_follow_limit = account_follow_limit
        self.stop = False
        self.driver = webdriver.Chrome(options = self.set_chrome_options())

    def set_chrome_options(self):
        chromedriver_autoinstaller.install(cwd=True)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.page_load_strategy = 'eager'
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        # chrome_options.add_argument("--headless")

        return chrome_options
    
    def login(self):
        self.driver.set_window_size(550, 450)
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
    
    def get_fan_account_url(self):
        WebDriverWait(self.driver, 45).until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='搜尋輸入']")))
        self.driver.find_element(By.XPATH, "//input[@aria-label='搜尋輸入']").send_keys(self.keyword)
        WebDriverWait(self.driver, 45).until(EC.presence_of_element_located((By.XPATH, "//div[@role='none']/a")))
        self.fan_account_url = [i.get_attribute("href") for i in self.driver.find_elements(By.XPATH, "//div[@role='none']/a")]

    def follow(self):
        send_follow = 0
        for url in self.fan_account_url:
            if self.stop:
                break
            if "explore/locations" in url:
                continue
            self.driver.get(url)
            WebDriverWait(self.driver, 45).until(EC.presence_of_element_located((By.XPATH, "//ul[@class='x1wzhzgj x78zum5 x1q0g3np x1l1ennw xz9dl7a x4uap5 xsag5q8 xkhd6sd']/li[2]/a")))
            self.driver.execute_script(f"window.scrollTo(0, {350});")
            self.driver.find_element(By.XPATH, "//ul[@class='x1wzhzgj x78zum5 x1q0g3np x1l1ennw xz9dl7a x4uap5 xsag5q8 xkhd6sd']/li[2]/a").click()
            WebDriverWait(self.driver, 45).until(EC.presence_of_element_located((By.CLASS_NAME, "_aano")))

            modal = self.driver.find_element(By.CLASS_NAME, "_aano")
            for i in range(10):
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
                time.sleep(5)

            accounts = self.driver.find_elements(By.XPATH, "//div[@class='_aano']/div[1]/div/div")
            same_fan_account_follow = 0
            for i in accounts:
                if send_follow < self.total_follow_limit:
                    if same_fan_account_follow < self.account_follow_limit:
                        print(i.find_element(By.XPATH, ".//div/div/div/div[1]//a").get_attribute("href"))
                        button = i.find_element(By.XPATH, ".//div/div/div/div[3]//button")
                        if button.find_element(By.XPATH, ".//div/div").text == "追蹤":
                            button.click()
                            print("send follow")
                            same_fan_account_follow += 1
                            send_follow += 1
                        else:
                            print(button.find_element(By.XPATH, ".//div/div").text)
                        time.sleep(random.uniform(10.0, 30.0))
                    else:
                        break
                else:
                    self.stop = True
        
    def run(self):
        self.login()
        self.get_fan_account_url()
        self.follow()
        self.driver.quit()

if __name__ == "__main__":
    cfg = ConfigParser()
    cfg.read("cfg.ini", encoding="utf-8")
    ID = cfg["ig_login_information"]["id"]
    PWD = cfg["ig_login_information"]["password"]
    KEYWORD = cfg["condition"]["keyword"]
    TOTAL_FOLLOW_LIMIT = int(cfg["condition"]["total_follow_limit"])
    ACCOUNT_FOLLOW_LIMIT = int(cfg["condition"]["account_follow_limit"])
    bot = AutoFollow(ID, PWD, KEYWORD, TOTAL_FOLLOW_LIMIT, ACCOUNT_FOLLOW_LIMIT)
    bot.run()