from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from .tools import check_func_args


def if_item_visible(args, browser, **kwargs):
    '''
    Checks if item is in the page (for example captcha image or textbox)

    Args:
        args (dict):
            path (string): path to check if its in the page
            if (int): True condition go
            else (int): False condition go, it's optional

        browser: browser

    Return:
        action index (int)
    '''

    if not check_func_args(args, ['path', 'if', 'else'],
                           [str, (int, str), (int, str)]):
        return 'Action Parameter Error'

    css_mode = kwargs['css_mode']
    path = args['path']
    if_action = int(args['if'])
    else_action = int(args['else'])

    try:
        if css_mode:
            element_present = EC.presence_of_element_located(
                (By.CSS_SELECTOR, path))
            WebDriverWait(browser, 5).until(element_present)

            elem = browser.find_element_by_css_selector(path)
        else:
            element_present = EC.presence_of_element_located(
                (By.XPATH, path))
            WebDriverWait(browser, 5).until(element_present)

            elem = browser.find_element_by_xpath(path)

        if elem is not None:
            # return True
            return if_action
        else:
            return else_action
    except:
        return else_action
