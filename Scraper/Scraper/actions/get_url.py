from urllib.parse import urlencode
from urllib.parse import urlsplit, urlunsplit

from .tools import check_func_args


def get_url(args, browser, **kwargs):
    '''
    Gets url

    Args:
        args (dict):
            url: base url
            params: dictionary contains key value
                    for GET parameters {'key': 'value'}

        browser: browser

    Return:
        Nothing
    '''

    if not check_func_args(args, ['url', 'params'], [str, (dict, list)]):
        return 'Parameter Error'

    base_url = args['url']
    params = args['params']

    # TODO: add check types

    # make url
    scheme, netloc, path, query_string, fragment = urlsplit(base_url)
    new_query_string = urlencode(params, doseq=True)

    base_url = urlunsplit((scheme, netloc, path, new_query_string, fragment))

    # get url
    try:
        browser.get(base_url)
        return 'OK'
    except:
        return 'ERR'
