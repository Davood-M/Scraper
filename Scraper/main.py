import os
import uuid
import json
import signal
import sys
import configparser
import multiprocessing
import time

from Scraper.scraper import scraper
from Scraper.tools.logger import logger, INFO, ERR

# import requirements
try:
    import logging
    from flask import Flask, request, abort
except:
    logger(ERR, 'Requirements Not Installed')


# handle exit signal
def signal_handler(signal, frame):
    # close processes
    for i in range(NUM_WORKERS):
        TASK_QUEUE.put('KILL')

    sys.exit(0)


def shutdown_server():
    # close browsers
    for i in range(NUM_WORKERS):
        TASK_QUEUE.put('KILL')

    time.sleep(3)

    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


# set loggin level
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# set Ctrl+c handle function
signal.signal(signal.SIGINT, signal_handler)

# create app
app = Flask('Scraper App')


# FUNCTIONS #
# insert new task
@app.route('/scraper/add_task', methods=['POST'])
def create_task():
    # check given task
    if not request.json or 'task' not in request.json:
        abort(400)

    # check KILL signal
    if request.json['task'] == 'KILL':
        shutdown_server()
        return json.dumps('Goodbye ...')

    # put task in queue
    tid = uuid.uuid4()
    task = {
        'task': request.json['task'],
        'tid': tid.__str__()
    }
    TASK_QUEUE.put((task, TASK_LOG))

    # add tid to task list and check size
    TASK_LIST.append(tid)
    if len(TASK_LIST) > TLOG_SIZE:
        TASK_LIST.pop(0)

    # create task and put in queue
    return json.dumps({
        'Result': 'Task Created',
        'Task_id': tid.__str__()
    })


@app.route('/scraper/check_status', methods=['POST'])
def chk_status():
    if not request.json or 'tid' not in request.json:
        abort(400)

    tid = request.json['tid']

    # check results
    if tid in TASK_LOG and TASK_LOG[tid]:
        return json.dumps({'status': 'Finished'})
    elif os.path.isfile('Results/' + tid + '.json'):
        return json.dumps({'status': 'Finished'})
    elif tid in TASK_LOG and not TASK_LOG[tid]:
        return json.dumps({'status': 'Running'})
    return json.dumps({'status': 'Task not Found'})


@app.route('/scraper/get_result', methods=['POST'])
def get_result():
    if not request.json or 'tid' not in request.json:
        abort(400)

    tid = request.json['tid']

    if os.path.isfile('Results/' + tid + '.json'):
        return json.dumps(json.load(open('Results/' + tid + '.json', 'r')))
    else:
        # check if task is running
        if tid in TASK_LOG and TASK_LOG[tid]:
            return json.dumps({'result': 'Task is Running!'})
        return json.dumps({'result': 'Invalid TID'})


def main():
    global TASK_QUEUE
    global VERBOSE
    global TLOG_SIZE
    global NUM_WORKERS
    global TASK_LOG
    global TASK_LIST
    global MANAGER

    # read config file
    config = configparser.ConfigParser()
    try:
        config.read('Configs/config.cfg')
    except:
        logger(ERR, 'Cannot Read Config File')
        return 1

    try:
        address = config.get('Server', 'ser_addr')
        port = config.getint('Server', 'ser_port')
    except:
        logger(ERR, 'Cannot Read Server Params')
        return 1

    try:
        debug = config.getboolean('Server', 'debug')
        NUM_WORKERS = config.getint('Process', 'num_workers')
        vrdisp_w = config.getint('VirtualDisp', 'width')
        vrdisp_h = config.getint('VirtualDisp', 'height')
        VERBOSE = config.getboolean('Development', 'verbose')
        TLOG_SIZE = config.getint('Server', 'max_task_log')
    except:
        logger(ERR, 'Config File Error')
        return 1

    # create workers
    TASK_QUEUE = multiprocessing.JoinableQueue()
    MANAGER = multiprocessing.Manager()
    TASK_LOG = MANAGER.dict()
    TASK_LIST = []

    if VERBOSE:
        logger(INFO, 'Running ...')

    if len(sys.argv) > 1 and sys.argv[1] == 'pyvd':
        logger(INFO, 'Running with PyVD')

        # create virtual Display
        try:
            from pyvirtualdisplay import Display

            display = Display(visible=0, size=(vrdisp_w, vrdisp_h))
            display.start()
        except:
            logger(ERR, 'Virtual Display Not Installed')
            exit()

    # create processes and start them
    workers = [scraper(TASK_QUEUE, VERBOSE) for i in range(NUM_WORKERS)]

    for w in workers:
        w.start()

    # create Results folder
    if not os.path.exists('Results'):
        os.makedirs('Results')

    # run app and listen
    app.run(debug=debug, host=address, port=port, use_reloader=False)

    # wait 1 second
    time.sleep(1)


# RUN APPLICATION
if __name__ == '__main__':
    main()
