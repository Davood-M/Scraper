import time


def wait_time(args, browser, **kwargs):
    '''
    Wait for N seconds :)

    Args:
        args (dict):
            time: time to wait

        browser: browser

    Return:
        Nothing
    '''

    ttw = args['time']
    time.sleep(ttw)

    return 'OK'
