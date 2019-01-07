import time
import re
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class woospider:
    def __init__(self,website="https://wootalk.today/"): # initial all woospider attribute
        self.__website = website # wootalk website
        self.__proxy_ip = []     # proxy ip pool
        self.__driver = None     # web driver
        #self.update_proxy()      # update proxy ip pool       
        self.set_driver()        # set driver property
        self.start_flag = False
        self.secret_key = None
        self.message_count = -1
        self.stranger_leave = False
        self.enter_room = False
        
    def update_proxy(self):
        option = webdriver.ChromeOptions()
        option.add_argument("headless")
        browser = webdriver.Chrome(chrome_options=option)
        browser.get("https://www.proxynova.com/proxy-server-list/country-tw/")
        browser.implicitly_wait(10)
        soup = BeautifulSoup(browser.page_source,'lxml')
        table = soup.find('tbody')
        data = table.find_all('tr')
        Ip = None
        Port = None
        for item in data:
            try:
                data = item.find_all('td')
                Ip = data[0].find('abbr').get_text().split(';')[1]
                Port = data[1].find('a').get_text()
                self.__proxy_ip.append(Ip.strip()+':'+Port)
            except:
                pass
        browser.close()

    def print_proxy(self):
        for i in self.__proxy_ip:
            print(i)
    
    def set_driver(self): # set driver proxy server and initial driver
        chrome_options = webdriver.ChromeOptions()
        """try:
            chrome_options.add_argument('--proxy-server=http://' + self.__proxy_ip.pop())
        except IndexError:
            self.update_proxy()
            chrome_options.add_argument('--proxy-server=http://' + self.__proxy_ip.pop())"""
        #self.__driver = webdriver.Chrome(chrome_options=chrome_options)
        self.__driver = webdriver.Chrome()
        try:
            self.__driver.minimize_window()
        except:
            pass
    
    def close_driver(self): # close driver
        self.__driver.close()
    
    def connect(self): # start driver
        self.__driver.get(self.__website)
        self.__driver.implicitly_wait(10)
        while self.__driver.title != "WooTalk 吾聊":
            self.close_driver()
            self.set_driver()
            self.__driver.get(self.__website)

    def set_secret(self, secret_key = None ):
        if secret_key != None:
            self.secret_key = secret_key
            self.__driver.get(self.__website+"key/"+self.secret_key)
        else:
            self.secret_key = secret_key
            self.__driver.get(self.__website)

    def start(self):
        try:
            self.__driver.minimize_window()
        except:
            pass
        self.stranger_leave = False
        self.message_count = -1
        cid = "startButton"
        self.__driver.find_element_by_id(cid).click()
        #link = None
        result = self.check_enter()
        if not self.enter_room:
            self.start_flag = False
            return result
        else:
            self.start_flag = True
            return result

    def leave(self):
        self.__driver.find_element_by_xpath("//input[@value='離開']").click()
        try:
            self.__driver.find_element_by_id("popup-yes").click()
        except:
            pass
        time.sleep(3)
        self.start_flag = False
        self.enter_room = False

    def send_message(self,message):
        if self.start_flag:
            try:
                locator = (By.ID, "sendButton")
                WebDriverWait(self.__driver, 0, 0.5).until(EC.element_to_be_clickable(locator))
                element = self.__driver.find_element_by_id("sendButton")
                button_type = element.find_element_by_tag_name('input').get_attribute('value')
                if button_type == "傳送":
                    textbox = self.__driver.find_element_by_xpath("//input[@placeholder='輸入訊息']")
                    textbox.send_keys(message)
                    element.click()
                
            except:
                pass
        else:
            raise Exception('The webspider doesn\' start.')
    
    def get_message(self,wait_scecond=0):
        message = None
        if self.start_flag:
            try:
                xpath = "//div[@mid='{}']".format(self.message_count+1)
                locator = (By.XPATH, xpath)
                WebDriverWait(self.__driver, wait_scecond, 0.5).until(EC.presence_of_element_located(locator))
                message = self.__driver.find_element_by_xpath(xpath).text
                message = re.match(r'陌生人：(.*)\n\(.*\)',message,re.S)
                if message:
                    message = message.group(1)
                else:
                    message = None
            except TimeoutException:
                message = None
        if message != None:
            self.message_count +=1
        return message
    
    def change_secret(self,secret_key = None):
        if secret_key:
            self.secret_key = secret_key
            self.__driver.get(self.__website+"key/"+self.secret_key)
        else:
            self.secret_key = secret_key
            self.__driver.get(self.__website)
    
    def check_stranger(self):
        # https://goo.gl/sILzKT
        soup = BeautifulSoup(self.__driver.page_source,'lxml')
        text = soup.find_all('div',{'class':'system text '})
        try:
            text = text[-1]
            message = text.get_text()
            if message == "系統訊息：對方離開了，請按離開按鈕回到首頁其他人在聊什麼?我想看看尋人啟事":
                self.stranger_leave = True
            else:
                self.stranger_leave = False
        except:
            self.stranger_leave = False
        return self.stranger_leave
    
    def check_enter(self):
        # https://goo.gl/sILzKT
        text = []
        current_time = time.time()
        pass_time = 0
        link = None
        try:
            locator = (By.LINK_TEXT, '開啟此連結')
            WebDriverWait(self.__driver, 5, 0.5).until(EC.presence_of_element_located(locator))
            link = self.__driver.find_element_by_link_text('開啟此連結').get_attribute('href')
        except TimeoutException:
            pass
        if link:
            return 'wait'
        
        while pass_time < 20:
            soup = BeautifulSoup(self.__driver.page_source,'lxml')
            text = soup.find_all('div',{'class':'system text '})
            pass_time = time.time() - current_time
            try:
                text = text[2]
                self.enter_room = True
                return None
            except:
                pass
                
        try:
            text = text[2]
            self.enter_room = True
            return None
        except:
            self.enter_room = False
            return 'long'
    
    def maximize(self):
        self.__driver.maximize_window()