from datetime import datetime
from termcolor import colored


INFO = 1  # INFO LOG TYPE
WARN = 2  # WARNNING LOG TYPE
ERR = 3   # ERROR LOG TYPE

# LOG_TYPES + COLOUR TABLES
_log_types = {INFO: "INFO", WARN: "WARNING", ERR: "ERROR"}
_colours = {ERR: "red", WARN: "yellow", INFO: "blue"}
_custom_colors = {'green': 'green', 'cyan': 'cyan', 'magenta': 'magenta'}


# A CUSTOM EXCEPTION CLASS; WE MAY MODFY IT IN THE FUTURE
class Logger_Exception(Exception):
    pass


# MESSAGE MUST BE A STRING
def logger(log_type, message, custom_color=''):
    """ CUSTOM LOGGER """

    if log_type not in (INFO, WARN, ERR):
        raise Logger_Exception("Log type must be of 'WARN', 'INFO' and 'ERR'")

    if not isinstance(message, str):
        raise Logger_Exception("Message must be a 'string'")

    if len(message) < 1:
        raise Logger_Exception("Message can not be an empty string")

    timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())

    if custom_color == '':
        print((colored("[", "white") + colored(timestamp, "cyan") +
               colored("] :: [", "white") +
               colored(_log_types[log_type], _colours[log_type]) +
               colored("] ==> ", "white") +
               colored(message, _colours[log_type]))
              )
    elif custom_color in _custom_colors.keys():
        print((colored("[", "white") +
               colored(timestamp, "cyan") +
               colored("] :: [", "white") +
               colored(_log_types[log_type], _colours[log_type]) +
               colored("] ==> ", "white") +
               colored(message, _custom_colors[custom_color]))
              )
    else:
        print((colored("[", "white") +
               colored(timestamp, "cyan") +
               colored("] :: [", "white") +
               colored(_log_types[log_type], _colours[log_type]) +
               colored("] ==> ", "white") +
               colored(message, _colours[log_type]))
              )

    return


# test
if __name__ == '__main__':
    logger(INFO, 'INFO TEST...')
    logger(WARN, 'WARN TEST...')
    logger(ERR, 'ERROR TEST...')
    # logger(5, 'ERROR')
