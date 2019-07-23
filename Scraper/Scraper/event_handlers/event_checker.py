from ..tools.logger import logger, ERR
import json


class event_checker(object):
    def __init__(self, events_file, browser):
        '''
        Read events from file
        '''
        try:
            self.events = json.load(
                open(events_file, 'r')
            )
        except:
            logger(ERR, 'Cannot Open Events File')
            return None
        self.browser = browser

        self.functions = {
            'url': self.check_url,
            'id': self.if_visible,
            'is_equal': self.is_equal
        }

        while '_comment' in self.events:
            self.events.pop('_comment', None)

    def check_bad_event(self):
        '''
        Check for bad events that are in the file
        '''

        bad_events = []

        # get number of keys
        for ev_name, ev in self.events.items():
            # get number of event keys
            n_keys = 0
            n_conditions = 0

            if 'action' in ev:
                action = ev['action']
            else:
                action = ''

            for k in self.functions.keys():
                if k in ev and ev[k] != '':
                    n_keys += 1

            # get css mode if avail.
            if 'css_mode' in ev:
                css_mode = ev['css_mode']
            else:
                css_mode = True

            # now check each of available keys
            for k in self.functions.keys():
                if k in ev and ev[k] != '':
                    # run function
                    func = self.functions[k]
                    ret = func(ev[k], css_mode=css_mode)

                    print(func.__name__)
                    print(ret)

                    if ret:
                        n_conditions += 1

            # check conditions:
            if n_conditions == n_keys:
                # BAD STATE :(
                bad_events.append({ev_name: action})

        # return bad events
        return bad_events

    def is_equal(self, eq_dict, **kwargs):
        '''
        Checks if items in dictionary are equal to their values

        Return:
            boolean (True -> all are same and visible)
        '''

        if 'css_mode' in kwargs:
            css_mode = kwargs['css_mode']
        else:
            css_mode = True

        for k, v in eq_dict:
            try:
                if css_mode:
                    elem = self.browser.find_element_by_css_selector(k)
                else:
                    elem = self.browser.find_element_by_xpath(k)
            except:
                return False

            if elem is None or elem.text != v:
                return False
        return True

    def if_visible(self, id, **kwargs):
        '''
        Check if item is visible in the current page

        Return:
            boolean (True -> visible)
        '''
        if 'css_mode' in kwargs:
            css_mode = kwargs['css_mode']
        else:
            css_mode = True

        # check if item is visible
        try:
            if css_mode:
                elem = self.browser.find_element_by_css_selector(id)
            else:
                elem = self.browser.find_element_by_xpath(id)
        except Exception as e:
            print(e)
            return False

        if elem is not None:
            return True
        return False

    def check_url(self, url, **kwargs):
        '''
        Check browser url with given url

        Return:
            boolean (True -> equal)
        '''

        if self.browser.current_url == url:
            return True
        return False
