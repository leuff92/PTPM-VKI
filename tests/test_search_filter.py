import os
import unittest

from selenium import webdriver

from pages.search_filter_page import SearchFilterPage


HOUSE_RENT = ("Cash", "EXPENDITURE", "HouseRent", "1000")
BANK_INTERNET = ("Bank Savings", "EXPENDITURE", "InternetBill", "500")
CASH_INTERNET = ("Cash", "EXPENDITURE", "InternetBill", "1200")
SALARY = ("Bank Savings", "INCOME", "Salary", "5000")
POWER_BILL = ("Cash", "EXPENDITURE", "PowerBill", "200")
ALL_ROWS = [HOUSE_RENT, BANK_INTERNET, CASH_INTERNET, SALARY, POWER_BILL]


class TestSearchFilter(unittest.TestCase):
    def setUp(self):
        options = webdriver.ChromeOptions()
        #if os.environ.get("LAB6_SHOW_BROWSER") != "1":
       #     options.add_argument("--headless")
        options.add_argument("--window-size=1280,900")
        self.driver = webdriver.Chrome(options=options)
        try:
            self.driver.set_page_load_timeout(30)
            self.page = SearchFilterPage(self.driver)
            self.page.open()
        except Exception:
            self.driver.quit()
            raise

    def tearDown(self):
        try:
            self._take_screenshot()
        finally:
            self.driver.quit()

    def test_initial_results(self):
        self.assertEqual(self.page.read_results(), ALL_ROWS)

    def test_search_payee_by_partial_name(self):
        self.page.search_payee("internet")
        self.assertEqual(self.page.read_results(), [BANK_INTERNET, CASH_INTERNET])

    def test_search_payee_for_income(self):
        self.page.search_payee("Salary")
        self.assertEqual(self.page.read_results(), [SALARY])

    def test_filter_cash_account(self):
        self.page.select_account("Cash")
        self.assertEqual(self.page.read_results(), [HOUSE_RENT, CASH_INTERNET, POWER_BILL])

    def test_filter_bank_account(self):
        self.page.select_account("Bank Savings")
        self.assertEqual(self.page.read_results(), [BANK_INTERNET, SALARY])

    def test_filter_income_type(self):
        self.page.select_type("INCOME")
        self.assertEqual(self.page.read_results(), [SALARY])

    def test_filter_expenditure_type(self):
        self.page.select_type("EXPENDITURE")
        self.assertEqual(
            self.page.read_results(), [HOUSE_RENT, BANK_INTERNET, CASH_INTERNET, POWER_BILL]
        )

    def test_search_expenditure_payee(self):
        self.page.search_expenditure_payee("bill")
        self.assertEqual(self.page.read_results(), [BANK_INTERNET, CASH_INTERNET, POWER_BILL])

    def test_expenditure_search_excludes_income(self):
        self.page.search_expenditure_payee("Salary")
        self.assertEqual(self.page.read_results(), [])

    def test_combine_payee_account_and_type(self):
        self.page.search_payee("internet")
        self.page.select_account("Cash")
        self.page.select_type("EXPENDITURE")
        self.assertEqual(self.page.read_results(), [CASH_INTERNET])

    def test_no_results_for_unknown_payee(self):
        self.page.search_payee("unknown-payee-123")
        self.assertEqual(self.page.read_results(), [])

    def test_reset_all_filters(self):
        self.page.search_payee("internet")
        self.page.select_account("Bank Savings")
        self.page.select_type("EXPENDITURE")
        self.page.search_expenditure_payee("bill")
        self.assertEqual(self.page.read_results(), [BANK_INTERNET])

        self.page.reset_filters()

        self.assertEqual(self.page.read_results(), ALL_ROWS)
