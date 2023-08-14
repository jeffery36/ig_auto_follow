import time
import random
import json
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from configparser import ConfigParser


class AutoUnFollow:
    def __init__(self, id, pwd, number):
        self.id = id
        self.pwd = pwd
        self.number = number

        with open("send_follow_account.json", "r") as f:
            self.send_follow_account_dict = json.load(f)
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
    
    def unfollow(self):
        fail_unfallow = self.send_follow_account.copy()
        for i in range(self.number):
            try:
                url = self.send_follow_account[i]
            except:
                break
            self.driver.get(url)
            try:
                WebDriverWait(self.driver, 45).until(EC.presence_of_element_located((By.XPATH, "//div[@class='x6s0dn4 x78zum5 x1q0g3np xs83m0k xeuugli x1n2onr6']/div[1]/div/div/button")))
            except:
                if self.driver.find_element(By.XPATH, "//div[@class='x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh xbxaen2 x1u72gb5 x1t1ogtf x13zrc24 x1n2onr6 x1plvlek xryxfnj x1c4vz4f x2lah0s xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh xl56j7k']"):
                    print(f"此連結可能發生故障，或該頁面已遭移除: {url}")
            else:
                button = self.driver.find_element(By.XPATH, "//div[@class='x6s0dn4 x78zum5 x1q0g3np xs83m0k xeuugli x1n2onr6']/div[1]/div/div/button")
                follow_status = button.find_element(By.XPATH, ".//div/div[1]").text
                if follow_status != "追蹤":
                    button.click()
                    WebDriverWait(self.driver, 45).until(EC.presence_of_element_located((By.XPATH, "//div[@class='x7r02ix xf1ldfh x131esax xdajt7p xxfnqb6 xb88tzc xw2csxc x1odjw0f x5fp0pe']")))
                    time.sleep(1)
                    if follow_status == "追蹤中":
                        modal = self.driver.find_element(By.XPATH, "//div[@class='x7r02ix xf1ldfh x131esax xdajt7p xxfnqb6 xb88tzc xw2csxc x1odjw0f x5fp0pe']")
                        self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
                        time.sleep(0.5)
                        self.driver.find_element(By.XPATH, "//div[@class='x7r02ix xf1ldfh x131esax xdajt7p xxfnqb6 xb88tzc xw2csxc x1odjw0f x5fp0pe']/div/div/div/div[8]").click()
                    elif follow_status == "已送出請求":
                        self.driver.find_element(By.XPATH, "//button[@class='_a9-- _a9-_']").click()
            
            fail_unfallow.remove(url)
            time.sleep(random.uniform(5.0, 15.0))
        self.send_follow_account = fail_unfallow
    
    def run(self):
        self.login()
        time.sleep(3)
        self.unfollow()
        self.driver.quit()

        self.send_follow_account_dict[self.id] = self.send_follow_account
        with open("send_follow_account.json", "w") as f:
            json.dump(self.send_follow_account_dict, f, indent = 4)

if __name__ == "__main__":
    cfg = ConfigParser()
    cfg.read("cfg.ini", encoding="utf-8")
    ID = cfg["ig_login_information"]["id"]
    PWD = cfg["ig_login_information"]["password"]
    NUMBER = int(cfg["unfollow"]["number"])
    bot = AutoUnFollow(ID, PWD, NUMBER)
    bot.run()