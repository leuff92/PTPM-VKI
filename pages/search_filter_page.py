from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


class SearchFilterPage:
    _URL = "https://www.globalsqa.com/angularJs-protractor/SearchFilter/"
    _PAYEE = (By.ID, "input1")
    _ACCOUNT = (By.ID, "input2")
    _TYPE = (By.ID, "input3")
    _EXPENDITURE_PAYEE = (By.ID, "input4")
    _ROWS = (By.CSS_SELECTOR, "table tbody tr")
    _CELLS = (By.TAG_NAME, "td")

    def __init__(self, driver):
        self._driver = driver

    def open(self):
        try:
            self._load()
        except TimeoutException:
            self._load()

    def _load(self):
        self._driver.get(self._URL)
        WebDriverWait(self._driver, 15).until(
            EC.text_to_be_present_in_element(self._ACCOUNT, "Bank Savings"),
            message="Search Filter did not load its account options.",
        )

    def _set_text(self, locator, text):
        field = self._driver.find_element(*locator)
        field.send_keys(Keys.CONTROL, "a")
        field.send_keys(Keys.BACKSPACE)
        if text:
            field.send_keys(text)

    def search_payee(self, name):
        self._set_text(self._PAYEE, name)

    def select_account(self, name):
        Select(self._driver.find_element(*self._ACCOUNT)).select_by_visible_text(name)

    def select_type(self, transaction_type):
        Select(self._driver.find_element(*self._TYPE)).select_by_visible_text(
            transaction_type
        )

    def search_expenditure_payee(self, name):
        self._set_text(self._EXPENDITURE_PAYEE, name)

    def reset_filters(self):
        self.search_payee("")
        self.select_account("All Accounts")
        self.select_type("All Types")
        self.search_expenditure_payee("")

    def read_results(self):
        results = []
        for row in self._driver.find_elements(*self._ROWS):
            cells = row.find_elements(*self._CELLS)
            account, transaction_type, payee, amount = cells[1:]
            results.append((account.text, transaction_type.text, payee.text, amount.text))
        return results

    def _take_screenshot(self):
        if not self.driver:
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._testMethodName}_{timestamp}.png"
        path = os.path.join(SCREENSHOT_DIR, filename)
        try:
            self.driver.save_screenshot(path)
            print(f"\nScreenshot saved: {path}")
        except Exception as e:
            print(f"\nFailed to save screenshot: {e}")