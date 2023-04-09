from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
import os

user_name = "test42"
user_email = "test42@freemail.hu"
user_password = "1234Abc!"

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
        register_link = self.browser.find_element(By.XPATH, '//a[@href="#/register"]')
        register_link.click()

        username_input = self.browser.find_element(By.XPATH, '//input[@placeholder="Username"]')
        email_input = self.browser.find_element(By.XPATH, '//input[@placeholder="Email"]')
        password_input = self.browser.find_element(By.XPATH, '//input[@type="password"]')
        sign_up_btn = self.browser.find_element(By.XPATH, '//button[contains(text(), "Sign up")]')

        username_input.send_keys(user_name)
        email_input.send_keys(user_email)
        password_input.send_keys(user_password)

        sign_up_btn.click()

        WebDriverWait(self.browser, 3).until(EC.url_to_be('http://localhost:1667/#/'))

        modal_icon = self.browser.find_element(By.CSS_SELECTOR, '.swal-modal > .swal-icon--success')
        assert modal_icon.is_displayed()

        modal = self.browser.find_element(By.CSS_SELECTOR, '.swal-modal')
        ok_btn = self.browser.find_element(By.CSS_SELECTOR, '.swal-modal button.swal-button--confirm')
        ok_btn.click()
        WebDriverWait(self.browser, 3).until(EC.invisibility_of_element(modal))

    def login(self):
        login_link = self.browser.find_element(By.XPATH, '//a[@href="#/login"]')
        login_link.click()

        email_input = self.browser.find_element(By.XPATH, '//input[@placeholder="Email"]')
        password_input = self.browser.find_element(By.XPATH, '//input[@type="password"]')
        sign_in_btn = self.browser.find_element(By.XPATH, '//button[contains(text(), "Sign in")]')

        email_input.send_keys(user_email)
        password_input.send_keys(user_password)
        sign_in_btn.click()

        WebDriverWait(self.browser, 3).until(EC.url_to_be('http://localhost:1667/#/'))

    def test_login(self):
        self.login()

        username_nav = self.browser.find_element(By.XPATH, '//li/a[contains(text(), "' + user_name + '")]')
        assert username_nav.is_displayed()
    def test_new_article(self):
        self.login()
        new_article_link = self.browser.find_element(By.XPATH, '//a[@href="#/editor"]')
        new_article_link.click()
        WebDriverWait(self.browser, 3).until(EC.url_to_be('http://localhost:1667/#/editor'))
        article_title = self.browser.find_element(By.XPATH, '//input[@placeholder="Article Title"]')
        about = self.browser.find_element(By.XPATH, '//input[@placeholder="What\'s this article about?"]')
        article_text = self.browser.find_element(By.XPATH, '//textarea[@placeholder="Write your article (in markdown)"]')
        tag = self.browser.find_element(By.CSS_SELECTOR, 'input.ti-new-tag-input')
        publish_btn = self.browser.find_element(By.XPATH, '//button[@type="submit"]')

        article_title.send_keys('test')
        about.send_keys('testing')
        article_text.send_keys('this is a test article')
        tag.send_keys('test')
        article_text.click()
        tag.send_keys('article')
        publish_btn.click()

        WebDriverWait(self.browser, 3).until(EC.url_to_be('http://localhost:1667/#/articles/test'))
        actual_article_title = self.browser.find_element(By.CSS_SELECTOR, 'h1')
        assert actual_article_title.text == 'test'
