from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
import os


class TestConduit(object):

    def setup_method(self):
        self.is_ci = os.getenv("CI", 'False').lower() in ('true', '1', 't')
        s = Service(executable_path=ChromeDriverManager().install())
        o = Options()
        o.add_experimental_option("detach", True)
        if self.is_ci:
            o.add_argument('--headless')
            o.add_argument('--no-sandbox')
            o.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(service=s, options=o)
        URL = "http://localhost:1667/#/"
        self.browser.get(URL)

    def teardown_method(self):
        self.browser.quit()

    def accept_cookies(self):
        accept = self.browser.find_element(By.CLASS_NAME, 'cookie__bar__buttons__button--accept')
        accept.click()

    ## Cookie-k elfogadásának tesztelése
    def test_accept_cookies(self):
        self.accept_cookies()
        time.sleep(1)
        cookie_container = self.browser.find_elements(By.CSS_SELECTOR, 'footer > .container > #cookie-policy-panel')
        assert len(cookie_container) == 0

    def test_register(self):
        if not self.is_ci:
            return
        register_link = self.browser.find_element(By.XPATH, '//a[@href="#/register"]')
        register_link.click()

        username_input = self.browser.find_element(By.XPATH, '//input[@placeholder="Username"]')
        email_input = self.browser.find_element(By.XPATH, '//input[@placeholder="Email"]')
        password_input = self.browser.find_element(By.XPATH, '//input[@type="password"]')
        sign_up_btn = self.browser.find_element(By.XPATH, '//button[contains(text(), "Sign up")]')

        username_input.send_keys('test42')
        email_input.send_keys('test42@freemail.hu')
        password_input.send_keys('1234Abc!')

        sign_up_btn.click()

        WebDriverWait(self.browser, 3).until(EC.url_to_be('http://localhost:1667/#/'))
