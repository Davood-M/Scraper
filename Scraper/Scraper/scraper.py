# Main file for scraper Class
import json
import platform
import multiprocessing
import logging

from importlib import import_module

from .tools.check_tools import check_input
from .tools.logger import logger, ERR, INFO, WARN, _custom_colors
from .tools.click_on_elem import click_on_elem
from .event_handlers import event_checker
from .actions.auto_get_data import auto_get_data

try:
    from selenium import webdriver
    from selenium.webdriver.remote.remote_connection import LOGGER
except:
    logger(ERR, 'Requirements Not Installed')


class scraper(multiprocessing.Process):
    '''
    Scraper class
    '''

    def __init__(self, task_queue, verbose):
        '''
        Initializes one scraper process

        Args:
            task_queue: task queue
            verbose (bool): print INFO or not

        Returns:
            Nothing
        '''

        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.verbose = verbose

        # init actions
        self.web_actions = json.load(open('Configs/actions.json', 'r'))
        for i in self.web_actions.keys():
            if i[0] is '_':
                continue

            tmp_file = import_module(
                'Scraper.actions.' + self.web_actions[i]
            )
            self.web_actions[i] = getattr(tmp_file, self.web_actions[i])

        # inline actions -> flowchart related
        self.inline_actions = {
            'goto',
            'loop',
            'auto_get_data'
            # other inline actions
        }

        # init firefox driver
        LOGGER.setLevel(logging.WARNING)

        self.options = webdriver.FirefoxProfile()

        if platform.system() == 'Linux':
            # extension
            extensions = [
                'Scraper/driver/ImageBlock.xpi'
            ]

            self.driver_path = 'Scraper/driver/geckodriver'

            # disable Images and Flash
            self.options.set_preference('permissions.default.image', 2)
            self.options.set_preference(
                'dom.ipc.plugins.enabled.libflashplayer.so', 'false'
            )

            # add extensions to firefoxx
            for ext in extensions:
                self.options.add_extension(ext),
                self.options.set_preference(
                    'extensions.ImageBlock.currentVersion', '3.1'
                )
        else:
            logger(ERR, 'Platform Not Supported')

        # run
        self.browser = webdriver.Firefox(
            firefox_profile=self.options, executable_path=self.driver_path
        )
        self.browser.maximize_window()

        try:
            # initiate Global event checker
            self.gev_checker = event_checker.event_checker(
                'Configs/global_events.json',
                self.browser
            )

            if type(self.gev_checker) is str:
                logger(ERR, self.gev_checker)
        except:
            logger(WARN, 'Cannot Create Event Handler')
            self.gev_checker = None

        # initiate auto get data
        try:
            self.auto_getter = auto_get_data(
                'Configs/data_collector.json',
                self.browser
            )
        except:
            logger(WARN, 'Cannot Create Auto Collector')
            self.auto_getter = None

    def run(self):
        '''
        Run process and wait for task, saves result in a file
        named "tid.json"
        '''

        proc_name = self.name
        if self.verbose:
            logger(INFO, 'Im Ready: %s' % (proc_name))

        while True:
            next_task, task_log = self.task_queue.get()
            # False -> running, True -> finished
            task_log[next_task['tid']] = False

            # check task
            if next_task == 'KILL':
                # shutdown
                logger(INFO, '%s Terminating Process ...' % (proc_name))
                self.quit()
                self.task_queue.task_done()
                break

            # run task
            if self.verbose:
                logger(INFO, 'New Task %s' % (next_task['tid']))

            # fix \' character!
            task = json.dumps(next_task['task']).replace("'", '\'')
            answer = self.exectask(task)

            # remove cookies
            self.browser.delete_all_cookies()

            if self.verbose:
                logger(
                    INFO,
                    'Task %s Finished'
                    % (next_task['tid']), _custom_colors['cyan']
                )

            # save answer in file
            fout = open('Results/' + next_task['tid'] + '.json', 'w')
            json.dump(answer, fout)
            fout.close()

            task_log[next_task['tid']] = True
            self.task_queue.task_done()

    def exectask(self, inp):
        '''
        Execute task which is an array of actions

        Args:
            inp (string): JSON string which contains actions

        Returns:
            results (dict): dictionary which contains answers of each action
        '''
        results = {}
        if not check_input(inp):
            return 'INPUT ERROR'

        # get input data and process it
        inp = json.loads(inp)
        actions = inp['actions']

        # default options
        max_delay = 5
        site_events = None

        if 'options' in inp:
            if 'max_delay' in inp['options']:
                max_delay = inp['options']['max_delay']
            if 'site_events' in inp['options']:
                site_events = event_checker.event_checker(
                    inp['options']['site_events'],
                    self.browser
                )

        # actions
        actions = sorted(actions.items())
        actions_index = 0

        while actions_index < len(actions):
            bad_ev = False
            print(actions_index)
            print(len(actions))

            # check global events
            if self.gev_checker is not None:
                # check captcha event
                bad_events = self.gev_checker.check_bad_event()
            else:
                bad_events = []

            # check site events
            if site_events is not None:
                bad_events.extend(site_events.check_bad_event())

            # check bad events len
            if len(bad_events) > 0:
                # Report for now and take first action
                bad_ev = True
                ev_key = list(bad_events[0].keys())[0]
                action = bad_events[0][ev_key]
            else:
                # unpack
                action_no = actions[actions_index][0]
                action = actions[actions_index][1]

            # get method and arguments
            method = action['method'].lower()
            if 'args' in action:
                args = action['args']

            # check for comment
            if '_comment' in action:
                logger(INFO, 'Comment: %s' % (action['_comment']),
                       custom_color=_custom_colors['magenta'])

            # check for css_mode
            if 'css_mode' not in action or action['css_mode'] is False:
                css_mode = False
            else:
                css_mode = True

            # exec
            if method in self.web_actions:
                # execute web action
                ret = self.web_actions[method](
                    args, self.browser,
                    css_mode=css_mode, max_delay=max_delay)

                if not bad_ev:
                    results[action_no] = ret
                else:
                    msg = 'Bad Event Before %d' % (actions_index - 1)
                    results[ev_key] = [msg, ret]
            elif method in self.inline_actions:
                # check it
                if method == 'goto':
                    try:
                        actions_index = int(args[0])
                        error = True

                        # fix index
                        for ind, item in enumerate(actions):
                            if int(item[0]) == actions_index:
                                actions_index = ind
                                error = False
                                continue

                        if not error:
                            continue
                        else:
                            return 'GOTO ACTION ERROR'

                    except:
                        return 'GOTO ACTION ERROR'
                elif method == 'loop':
                    try:
                        actions_list = action['actions']
                        iterations = int(action['iters'])
                        click_on_next = action['click_on']

                        for it in range(iterations):
                            # exec loop -> recursive
                            input_pass = json.dumps({
                                'actions': actions_list
                            })

                            results['loop' + str(it)] = \
                                self.exectask(input_pass)

                            # click on
                            click_on_elem(
                                self.browser, click_on_next, css_mode
                            )
                    except:
                        return 'LOOP PARAMETER ERROR'
                elif method == 'auto_get_data':
                    ret = self.auto_getter.find_info()
                    print(ret)
                    if ret[0]:
                        results[actions_index] = ret[1]

            else:
                return 'MODULE NOT FOUND ERROR'

            # goto next action
            actions_index += 1

            # check for errors
            if ret == 'ERR' and not bad_ev:
                return "ACTION %d ERROR" % (actions_index - 1)
            elif bad_ev and ret == 'ERR':
                logger(WARN, 'Event Handling Failed')

        return results

    def quit(self):
        '''
        Quit browser
        '''

        self.browser.quit()
        return None
