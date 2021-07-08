from selenium import webdriver
from time import sleep
import pickle
import json
from pathlib import Path
import os
import dotenv

dotenv_file = os.path.join(Path(__file__).resolve().parent,'.env')
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)
else:
    exit()

class InstagramInfo():
    DRIVER_PATH = '../tools/chromedriver'

    def __init__(self, headless=False):
        self.total_followers = 0
        self.total_followings = 0
        self.all_followers = {}
        self.all_followings = {}

        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.headless = headless
        self.driver = webdriver.Chrome(executable_path=self.DRIVER_PATH, options=self.chrome_options)

        with open('dataFile.json') as data_file:
            data = json.load(data_file)

        self.are_cookies_saved = data['initialized']

    def login(self, username, password):
        if self.are_cookies_saved:
            self.load_cookies()
            print('cookies loaded\n')
            return

        try:
            self.driver.get("https://www.instagram.com/")
            sleep(3)

            self.driver.find_element_by_xpath('//input[@name = \"username\"]').send_keys(username)
            self.driver.find_element_by_xpath('//input[@name = \"password\"]').send_keys(password)
            self.driver.find_element_by_xpath('//button[@type = \"submit\"]').click()
            sleep(5)

            self.save_cookies()

            jsonData = {'initialized': True}

            with open('dataFile.json', 'w') as f:
                json.dump(jsonData, f, indent=2)

        except Exception as e:
            print(e)
            exit()

    def save_cookies(self):
        pickle.dump(self.driver.get_cookies(), open("cookies.txt", "wb"))

    def load_cookies(self):
        try:
            cookies = pickle.load(open("cookies.txt", "rb"))
            self.driver.delete_all_cookies()

            # have to be on a page before you can add any cookies, any page - does not matter which
            self.driver.get("https://instagram.com")
            for cookie in cookies:

                # Checks if the instance expiry a float
                if isinstance(cookie.get('expiry'), float):

                    # It converts expiry cookie to a int
                    cookie['expiry'] = int(cookie['expiry'])
                self.driver.add_cookie(cookie)

        except:
            return False

    def followings(self):
        self.all_followings = {}

        self.driver.get('https://www.instagram.com/piyu5hkumar/')
        sleep(2)

        self.driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a').click()
        sleep(1.5)

        self.driver.execute_script('''
            followings = document.getElementsByClassName('isgrP')[0];
        ''')

        previous_height = self.driver.execute_script('''
            return followings.scrollHeight;
        ''')

        while True:
            self.driver.execute_script('''
                followings.scrollTo(0, followings.scrollHeight);
            ''')
            sleep(1)
            new_height = self.driver.execute_script('''
                return followings.scrollHeight;
            ''')
            if new_height == previous_height:
                break
            previous_height = new_height

        sleep(1)
        li = self.driver.find_element_by_class_name('PZuss')

        items = li.find_elements_by_tag_name('li')

        for li_item in items:
            name_div = li_item.find_elements_by_tag_name('a')
            if len(name_div) > 1:
                name = name_div[1].get_attribute('innerHTML')
                if name not in self.all_followings:
                    self.all_followings[name] = True

        self.total_followings = len(self.all_followings)

    def followers(self):
        self.all_followers = {}

        self.driver.get('https://www.instagram.com/piyu5hkumar/')
        sleep(2)

        self.driver.find_element_by_xpath(
            '/html/body/div[1]/section/main/div/header/section/ul/li[2]/a'
        ).click()
        sleep(1.5)

        self.driver.execute_script('''
            followers = document.getElementsByClassName('isgrP')[0];
        ''')

        previous_height = self.driver.execute_script(
            'return followers.scrollHeight')
        while True:
            self.driver.execute_script('''
                followers.scrollTo(0, followers.scrollHeight)
            ''')
            sleep(1)
            new_height = self.driver.execute_script('''
                return followers.scrollHeight
            ''')
            if new_height == previous_height:
                break
            previous_height = new_height

        sleep(1)

        li = self.driver.find_element_by_class_name('PZuss')

        items = li.find_elements_by_tag_name('li')

        for li_item in items:
            name_div = li_item.find_elements_by_tag_name('a')
            if len(name_div) > 1:
                name = name_div[1].get_attribute('innerHTML')
                if name not in self.all_followers:
                    self.all_followers[name] = True

        self.total_followers = len(self.all_followers)

    def analyze(self):
        self.followers()
        self.followings()
        print('total followings:', self.total_followings)
        print('total followers:', self.total_followers)

    def not_following_back(self):
        for following in self.all_followings:
            if following not in self.all_followers:
                print(f'{following} does\'nt follow you back')

    def not_follow_back(self):
        for follower in self.all_followers:
            if follower not in self.all_followings:
                print(f'you are not following {follower} back')

instagram_info = InstagramInfo()
instagram_info.login(os.environ.get('USER_NAME'), os.environ.get('PASSWORD'))
instagram_info.analyze()
instagram_info.not_following_back()



