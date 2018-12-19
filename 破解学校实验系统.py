import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chaojiying import Chaojiying

USERNAME=2017221005024
PASSWORD = '我的密码不告诉你'

CHAOJIYING_USERNAME = '957001934'
CHAOJIYING_PASSWORD = '我的密码不告诉你'
CHAOJIYING_SOFT_ID =897825
CHAOJIYING_KIND = 9004


class CrackTouClick():
    def __init__(self):
        self.url = 'https://ostec.uestc.edu.cn/authcas/login?service=http://202.115.16.61/eems/Login/doLogin'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.username=USERNAME
        self.password = PASSWORD
        self.chaojiying = Chaojiying(CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID)

    def open(self):
        self.browser.maximize_window()
        self.browser.get(self.url)
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'username')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'password')))
        username.send_keys(self.username)
        password.send_keys(self.password)

    def get_touclick_button(self):#返回登陆按钮
        button = self.wait.until(EC.element_to_be_clickable((By.ID,'action-form-submit')))
        return button

    def get_touclick_element(self):#获得验证码对象
        self.wait.until(EC.presence_of_all_elements_located)
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="captcha-master"]')))
        return element

    def get_position(self):#获取验证码位置
        element = self.get_touclick_element()
        time.sleep(5)
        location = element.location
        size = element.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)

    def get_screenshot(self):#得到网页截图
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_touclick_image(self, name='captcha.png'):#获取验证码图片
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def get_points(self, captcha_result):
        #得到位置点
        groups = captcha_result.get('pic_str').split('|')
        locations = [[int(number) for number in group.split(',')] for group in groups]
        return locations

    def touch_click_words(self, locations):
        for location in locations:
            print(location)
            ActionChains(self.browser).move_to_element_with_offset(self.get_touclick_element(), location[0],
                                                                   location[1]).click().perform()
            time.sleep(10)

    def touch_click_verify(self):#点击提交验证
        button = self.wait.until(EC.element_to_be_clickable((By.ID,'captcha-control-submit')))
        return button

    def crack(self):
        self.open()
        # 点击登陆按钮
        button = self.get_touclick_button()
        button.click()
        # 获取验证码图片
        image = self.get_touclick_image(name='captcha.png')
        bytes_array = BytesIO()
        image.save(bytes_array, format='PNG')
        # 识别验证码
        result = self.chaojiying.post_pic(bytes_array.getvalue(), CHAOJIYING_KIND)
        print(result)
        locations = self.get_points(result)
        self.touch_click_words(locations)
        button_tijiao=self.touch_click_verify()
        button_tijiao.click()
if __name__ == '__main__':
    crack = CrackTouClick()
    crack.crack()
