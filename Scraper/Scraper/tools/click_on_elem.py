

def click_on_elem(browser, elem, css_mode):
    if elem == '':
        return None

    # search
    try:
        if css_mode:
            click_elem = browser.find_element_by_css_selector(elem)
        else:
            click_elem = browser.find_element_by_xpath(elem)
    except:
        return None

    try:
        click_elem.click()
    except:
        return None

    return None
