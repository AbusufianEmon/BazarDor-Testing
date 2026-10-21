import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException

BASE_URL = "https://bazar-dor-ir-obot.vercel.app"


def open_home(d, tries=4):
    for attempt in range(1, tries + 1):
        try:
            d.get(BASE_URL)
            return
        except WebDriverException:
            if attempt == tries:
                raise
            time.sleep(5)


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.page_load_strategy = "eager"
    d = webdriver.Chrome(options=options)
    try:
        d.maximize_window()
        d.set_page_load_timeout(30)
        open_home(d)
        yield d
    finally:
        d.quit()


def wait_for(driver, condition, seconds=10):
    return WebDriverWait(
        driver, seconds, ignored_exceptions=(StaleElementReferenceException,)
    ).until(condition)


def click_link(driver, path):
    selector = f"a[href$='{path}']"
    link = wait_for(driver, EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
    link.click()


def test_home_page_loads(driver):
    assert "বাজার দর" in driver.title


def test_signin_button_opens_signin_page(driver):
    click_link(driver, "/signin")
    wait_for(driver, EC.url_contains("/signin"))
    assert "/signin" in driver.current_url


def test_signup_button_opens_signup_page(driver):
    click_link(driver, "/signup")
    wait_for(driver, EC.url_contains("/signup"))
    assert "/signup" in driver.current_url


@pytest.mark.parametrize("slug", [
    "chal", "dal", "tel", "sobji", "mach", "mangsho", "dim-dui", "mosla",
])
def test_category_buttons_open_category_page(driver, slug):
    click_link(driver, f"/category/{slug}")
    wait_for(driver, EC.url_contains(f"/category/{slug}"))
    assert f"/category/{slug}" in driver.current_url


def test_product_page_requires_login(driver):
    click_link(driver, "/product/peyaj")
    wait_for(driver, EC.url_contains("/signin"))
    assert "/signin" in driver.current_url


def test_wrong_password_does_not_log_in(driver):
    driver.get(BASE_URL + "/signin")
    email = wait_for(driver, EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "input[type='email']")))
    password = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    email.send_keys("wrong.user@example.com")
    password.send_keys("not-the-real-password")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)
    assert "/signin" in driver.current_url