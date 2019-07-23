import re
import json

from .get_data import get_data


class auto_get_data(object):

    def __init__(self, info_filename, browser):
        '''
        Loads file
        '''

        self.sites = {}
        self.browser = browser
        sites = json.load(open(info_filename, 'r'))

        for site in list(sites.keys()):
            # change / and *
            new_site = site.replace('/', '\\/')
            new_site = new_site.replace('*', '.*')
            new_site = new_site.replace('?', '\\?')

            self.sites[new_site] = sites[site]

        import pprint
        pprint.pprint(self.sites)

    def find_info(self):
        '''
        Finds useful info according to the file rules

        Returns:
            [boolean, list/None]
            * boolean: True -> found some data
            * list/None: if data found, return a list, else None
        '''

        for site in self.sites:
            search = re.search(site, self.browser.current_url)

            if search:
                # get related data
                return [
                    True,
                    get_data(
                        self.sites[site]['elements'],
                        self.browser,
                        css_mode=True,
                        max_delay=5
                    )
                ]

        return [False, None]
