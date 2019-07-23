import base64
import time
import json
import requests
import urllib.request as reqpic
import configparser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from ..tools.logger import logger, ERR


def solve_captcha(args, browser, **kwargs):
    '''
    Solves captcha using it's micro-service

    Args:
        args:
            image xpath/css (str): image address
            textbox xpath/css (str): insert text
            button xpath/css (str): button to submit result for captcha
        browser: browser

    Return:
        Success or Fail
    '''

    image_path = args['image']
    button_path = args['button']
    text_path = args['textbox']

    # get optional vars
    css_mode = kwargs['css_mode']
    max_delay = kwargs['max_delay']

    # check if captcha microservice is running
    config = configparser.ConfigParser()
    try:
        config.read('Configs/config.cfg')
        address = config.get('CaptchaMS', 'ser_addr')
        port = config.getint('CaptchaMS', 'ser_port')
        url = 'http://' + address + ':' + str(port)
        provider = config.get('CaptchaMS', 'provider')
        username = config.get('CaptchaMS', 'username')
        password = config.get('CaptchaMS', 'password')
    except:
        logger(ERR, 'Config File Error')
        return 'Config File Error'

    try:
        requests.get(url + '/version')
    except:
        logger(ERR, 'Service Not Running')
        return 'Service Not Running'

    # get image
    try:
        if not css_mode:
            # search by xpath
            element_present = EC.presence_of_element_located(
                (By.XPATH, image_path))
            WebDriverWait(browser, max_delay).until(element_present)

            img = browser.find_element_by_xpath(image_path)
        else:
            # search by css selector
            element_present = EC.presence_of_element_located(
                (By.CSS_SELECTOR, image_path))
            WebDriverWait(browser, max_delay).until(element_present)
            img = browser.find_element_by_css_selector(image_path)

        src = img.get_attribute('src')

        # get image and convert to base64
        img = base64.b64encode(reqpic.urlopen(src).read())
        img = img.decode('utf-8')

        # send image to micro-service and wait
        task = '{ "method": "captcha", "args":{"provider": "' + provider + '", \
                "config": {"image": "' + img + '", "username": \
                "' + username + '","password": "' + password + '"}}}'

        img_text = requests.post(url + '/create-task',
                                 data=task,
                                 headers={'Content-Type': 'application/json'})
        if img_text.status_code != 200:
            return 'Create Task Error'
    except:
        return 'IMG Not Found'

    # wait for task to complete
    task_id = img_text.text

    try:
        r = requests.post(url + '/check-status', data=task_id,
                          headers={'Content-Type': 'application/json'})
        counter = 0

        while counter < 30 and \
                json.loads(r.text)['status'] not in ['failed', 'finished']:

            r = requests.post(url + '/check-status', data=task_id,
                              headers={'Content-Type': 'application/json'})

            counter += 1
            time.sleep(1)
    except:
        return 'Connection Error'

    # task is finished, fetch results
    r = requests.post(url + '/fetch-results', data=task_id,
                      headers={'Content-Type': 'application/json'})
    try:
        capt_text = json.loads(r.text)['results']['results'][1]
    except:
        return 'Captcha Error'

    # insert text and submit
    try:
        if not css_mode:
            # search by xpath
            element_present = EC.presence_of_element_located(
                (By.XPATH, text_path))
            WebDriverWait(browser, max_delay).until(element_present)

            textbox = browser.find_element_by_xpath(text_path)
        else:
            # search by css selector
            element_present = EC.presence_of_element_located(
                (By.CSS_SELECTOR, text_path))
            WebDriverWait(browser, max_delay).until(element_present)
            textbox = browser.find_element_by_css_selector(text_path)

        textbox.send_keys(capt_text)
    except:
        return 'TextBox Not Found'

    # not click!
    if button_path == '':
        return 'OK'

    # submit
    try:
        if not css_mode:
            # search by xpath
            element_present = EC.presence_of_element_located(
                (By.XPATH, button_path))
            WebDriverWait(browser, max_delay).until(element_present)

            textbox = browser.find_element_by_xpath(button_path)
        else:
            # search by css selector
            element_present = EC.presence_of_element_located(
                (By.CSS_SELECTOR, button_path))
            WebDriverWait(browser, max_delay).until(element_present)
            textbox = browser.find_element_by_css_selector(button_path)

        textbox.click()
    except:
        return 'Button Not Found'

    return 'OK'
