""" Importok: """

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
        url = "http://localhost:1667/#/"
        self.browser.get(url)

    def teardown_method(self):
        self.browser.quit()

    def accept_cookies(self):
        accept = self.browser.find_element(By.CLASS_NAME, 'cookie__bar__buttons__button--accept')
        accept.click()

    """ TC1: Adatkezelési nyilatkozat használata (cookie-k elfogadása) """

    def test_accept_cookies(self):
        self.accept_cookies()
        time.sleep(1)
        cookie_container = self.browser.find_elements(By.CSS_SELECTOR, 'footer > .container > #cookie-policy-panel')
        assert len(cookie_container) == 0

    """ TC2: Regisztráció helyes adatokkal """

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

    """ TC3: bejelentkezés helyes adatokkal """

    def test_login(self):
        self.login()

        username_nav = self.browser.find_element(By.XPATH, '//li/a[contains(text(), "' + user_name + '")]')
        assert username_nav.is_displayed()

    def create_article(self, title, about, text, tags):
        self.login()
        new_article_link = self.browser.find_element(By.XPATH, '//a[@href="#/editor"]')
        new_article_link.click()
        WebDriverWait(self.browser, 3).until(EC.url_to_be('http://localhost:1667/#/editor'))
        article_title = self.browser.find_element(By.XPATH, '//input[@placeholder="Article Title"]')
        about_text = self.browser.find_element(By.XPATH, '//input[@placeholder="What\'s this article about?"]')
        article_text = self.browser.find_element(By.XPATH,
                                                 '//textarea[@placeholder="Write your article (in markdown)"]')
        tag_input = self.browser.find_element(By.CSS_SELECTOR, 'input.ti-new-tag-input')
        publish_btn = self.browser.find_element(By.XPATH, '//button[@type="submit"]')

        article_title.send_keys(title)
        about_text.send_keys(about)
        article_text.send_keys(text)
        for tag in tags:
            tag_input.send_keys(tag)
            article_text.click()
        publish_btn.click()
        WebDriverWait(self.browser, 3).until(EC.url_matches('http://localhost:1667/#/articles'))

    def test_new_article(self):
        self.create_article('test1', 'about test', 'this is a test article', ['test', 'article'])
        actual_article_title = self.browser.find_element(By.CSS_SELECTOR, 'h1')
        assert actual_article_title.text == 'test1'
        actual_author = self.browser.find_element(By.CSS_SELECTOR, '.article-meta .author')
        assert actual_author.text == user_name
        actual_article_content = self.browser.find_element(By.CSS_SELECTOR, '.article-content div div')
        assert actual_article_content.text == 'this is a test article'
        actual_tags = self.browser.find_element(By.CSS_SELECTOR, '.article-content .tag-list')
        assert actual_tags.text == 'testarticle'

    def test_edit_article(self):
        self.create_article('test-edit', 'test-edit about', 'this is a test article', ['edit'])
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Edit Article"]')))

        edit_btn = self.browser.find_element(By.XPATH, '//*[contains(text(), "Edit Article"]')
        edit_btn.click()
        WebDriverWait(self.browser, 5).until(EC.url_matches('http://localhost:1667/#/editor'))
        article_text = self.browser.find_element(By.XPATH, '//textarea[@placeholder="Write your article (in markdown)"]')
        article_text.send_keys(' which was modified')
        publish_btn = self.browser.find_element(By.XPATH, '//button[@type="submit"]')
        publish_btn.click()
        WebDriverWait(self.browser, 5).until(EC.url_to_be('http://localhost:1667/#/articles/test'))

        modified_article_text = self.browser.find_element(By.CSS_SELECTOR, '.article-content div div')
        assert modified_article_text.text == 'this is a test article which was modified'

    def test_delete_article(self):
        self.create_article('test delete', 'about delete', 'this is an article that must be deleted', ['delete', 'me'])
        delete_btn = self.browser.find_element(By.CSS_SELECTOR, '.btn-outline-danger')
        WebDriverWait(self.browser, 3).until(EC.visibility_of(delete_btn))
        delete_btn.click()
        WebDriverWait(self.browser, 3).until(
            EC.presence_of_element_located((By.XPATH, '//div[text()="Deleted the article. Going home..."]')))
        WebDriverWait(self.browser, 3).until(EC.url_to_be('http://localhost:1667/#/'))
