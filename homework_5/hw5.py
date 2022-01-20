from gettext import find
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

driver = webdriver.Chrome()

url = 'https://www.mvideo.ru/'

driver.get(url)
driver.implicitly_wait(10)
driver.maximize_window()


def page_down():
    driver.find_element(
        By.XPATH, '//a[contains(@class, "logo")]').send_keys(Keys.PAGE_DOWN)


def find_button():
    try:
        el = driver.find_element(
            By.XPATH, '//span[contains(text(), "В тренде")]/../..')
        el.click()
    except Exception:
        page_down()
        find_button()


def find_cards():
    product_cards = driver.find_element(
        By.TAG_NAME, 'mvid-product-cards-group')
    card_names = product_cards.find_elements(
        By.XPATH, '//div[contains(@class, "product-mini-card__name")]')
    card_prices = product_cards.find_elements(
        By.XPATH, '//div[contains(@class, "product-mini-card__price")]')
    for card_name, card_price in zip(card_names, card_prices):
        url = card_name.find_element(By.XPATH, './/div/a')
        product_card = {
            '_id': url.get_attribute('href'),
            'card_name': card_name.find_element(By.XPATH, './/div/a/div').text,
            'card_price': int(card_price.find_element(By.XPATH, './/span[contains(@class,"price__main-value")]').text.replace('\xa0', '').replace(' ', ''))
        }
        try:
            products.insert_one(product_card)
        except DuplicateKeyError:
            print('Товар в уже в базе')


find_button()

client = MongoClient("localhost", 27017)
db = client["product_cards"]
products = db.products

find_cards()

driver.quit()
