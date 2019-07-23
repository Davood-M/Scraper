import json
from .logger import logger, ERR


def check_input(inp):
    '''
    Check if json str is valid

    Args:
        JSON string
    Return:
        True | False
    '''

    # check if its valid
    try:
        json_obj = json.loads(inp)
    except:
        logger(ERR, 'Input is not JSON string (check actions)')
        return False

    # check Args
    keys = ['actions']

    for k in keys:
        if k not in json_obj:
            logger(ERR, '%s key is not present in input' % (k))
            return False

    # check actions
    for k in list(json_obj['actions'].keys()):
        if 'method' not in json_obj['actions'][k]:
            logger(ERR, 'Check action parameters')
            return False
    return True
