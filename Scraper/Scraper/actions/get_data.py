from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def has_attribute(elem, attr):
    try:
        elem.get_attribute(attr)
        return True
    except:
        return False


def get_data(args, browser, **kwargs):
    '''
    Gets data from web page elements texts

    Args:
        args (list): contains array of xpath strings
        css_mode (bool): address type
        browser: browser

    Return:
        dictionary of gathered data
    '''

    if type(args) is not list:
        return 'Parameter Error'

    css_mode = kwargs['css_mode']
    max_delay = kwargs['max_delay']
    data = {}

    # get data
    for index, path in enumerate(args):
        data[index] = []

        try:
            # check address mode
            if css_mode:
                # wait for it
                element_present = EC.presence_of_element_located(
                    (By.CSS_SELECTOR, path))
                WebDriverWait(browser, max_delay).until(element_present)

                # go
                for elem in browser.find_elements_by_css_selector(path):
                    if has_attribute(elem, 'href'):
                        data[index].append([
                            elem.text,
                            elem.get_attribute('href')])
                    elif has_attribute(elem, 'src'):
                        data[index].append([
                            elem.text,
                            elem.get_attribute('src')])
                    else:
                        data[index].append(elem.text)
            else:
                # wait for it
                element_present = EC.presence_of_element_located(
                    (By.XPATH, path))
                WebDriverWait(browser, max_delay).until(element_present)

                # go
                for elem in browser.find_elements_by_xpath(path):
                    if has_attribute(elem, 'href'):
                        data[index].append([
                            elem.text,
                            elem.get_attribute('href')])
                    elif has_attribute(elem, 'src'):
                        data[index].append([
                            elem.text,
                            elem.get_attribute('src')])
                    else:
                        data[index].append(elem.text)

        except TimeoutException:
            data[index] = 'Timeout'

        except:
            data[index] = 'XPath Not Found'

    return data
