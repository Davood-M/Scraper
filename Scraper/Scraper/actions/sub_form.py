import time
import random

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from .tools import check_func_args


def sub_form(args, browser, **kwargs):
    '''
    Fills and submits form

    Args:
        args:
            input_dict: input dictionary contains {'xpath': 'input value'}
            button: xpath of button to press

        browser: browser

    Return:
        Success or Fail
    '''

    # check args
    check_func_args(args, ['input_dict', 'button'], [dict, str])

    input_dict = args['input_dict']
    button_xpath = args['button']

    css_mode = kwargs['css_mode']
    max_delay = kwargs['max_delay']

    # fill form
    error = False

    for input_path, value in input_dict.items():
        # find element
        try:
            if not css_mode:
                # search by xpath
                element_present = EC.presence_of_element_located(
                    (By.XPATH, input_path))
                WebDriverWait(browser, max_delay).until(element_present)

                elem = browser.find_element_by_xpath(input_path)
            else:
                # search by css selector
                element_present = EC.presence_of_element_located(
                    (By.CSS_SELECTOR, input_path))
                WebDriverWait(browser, max_delay).until(element_present)
                elem = browser.find_element_by_css_selector(input_path)

            # put value
            for ch in value:
                elem.send_keys(ch)
                if random.random() < 0.5:
                    time.sleep(random.random() / 10.0)
                else:
                    time.sleep(random.random() / 100.0)
        except:
            error = True
            break

    if error:
        return 'ERR'

    # click (can be optional)
    if button_xpath != '':
        # wait for button if it's dynamic
        try:
            if not css_mode:
                element_present = EC.presence_of_element_located(
                    (By.XPATH, button_xpath))
                WebDriverWait(browser, max_delay).until(element_present)

                button_elem = browser.find_element_by_xpath(button_xpath)
            else:
                element_present = EC.presence_of_element_located(
                    (By.CSS_SELECTOR, button_xpath))
                WebDriverWait(browser, max_delay).until(element_present)

                button_elem = browser.find_element_by_css_selector(
                    button_xpath)

        except:
            return 'Item Not Found'

        # click
        try:
            X = random.randint(1, 10)
            Y = random.randint(1, 10)

            action = ActionChains(browser)
            action.move_to_element_with_offset(button_elem, X, Y)
            action.click()
            action.perform()
        except:
            browser.execute_script("arguments[0].click();", button_elem)

    return 'OK'
