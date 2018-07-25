from multiprocessing import Process, Queue as PQueue, Value
from schedule_jobs.core.helper import underline2hump
from pprint import pprint
from typing import Union
import schedule
import logging
import time
import os


class App(object):
    """
    计划任务
    :ivar _logger
    :ivar _worker_num
    :ivar _jobs_module
    """

    logger: Union[Value, None] = None
    jobs_module: Union[Value, None] = None

    def __init__(self, log_level: int = logging.DEBUG, log_file_path: Union[None, str] = None, worker_num: int = 4,
                 jobs_module: str = 'jobs', app_name: Union[None, str] = None):
        handlers = []
        console = logging.StreamHandler()
        console.setLevel(log_level)
        handlers.append(console)

        if log_file_path is not None:
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(log_level)
            handlers.append(file_handler)
        logging.basicConfig(level=log_level, handlers=handlers)
        self._logger = logging.getLogger(app_name if app_name is not None else __name__)
        self._worker_num = worker_num
        self._jobs_module = jobs_module

    def _worker_main(worker_no: int, jobs_module_name: str, queue: PQueue, logger: logging.Logger):
        """
        :param jobs_module_name:
        :param queue:
        :param logger:
        :return:
        """
        print('worker no:', worker_no, ' starting...')
        jobs_module = __import__(jobs_module_name)
        module_path = getattr(jobs_module, '__path__')[0]
        module_names = [v.replace('.py', '') for v in os.listdir(module_path) if 'job.py' in v]
        jobs_map = {}
        for v in module_names:
            try:
                job_module = __import__(jobs_module_name + '.' + v)
                cls_name = underline2hump(v)
                jobs_map[v] = (cls_name, job_module)
            except (ImportError, AttributeError) as e:
                print(e.__repr__())
            except Exception as e:
                print(e.__repr__())
        while 1:
            job_name = queue.get()
            job = getattr(getattr(jobs_map[job_name][1], job_name), jobs_map[job_name][0])
            job_obj = job(logger)
            job_obj.run(worker_no)

    def schedule(self, daemon: bool = False):
        """
        计划
        :return:
        """
        jobs_module = __import__(self._jobs_module)
        module_path = getattr(jobs_module, '__path__')[0]
        module_names = [v.replace('.py', '') for v in os.listdir(module_path) if 'job.py' in v]
        pprint(module_names)
        job_queue = PQueue(20)
        print("daemon: %d" % daemon)
        for v in module_names:
            try:
                job_module = __import__(self._jobs_module + '.' + v)
                cls_name = underline2hump(v)
                job = getattr(getattr(job_module, v), cls_name)
                job_obj = job(self._logger)
                schedule_obj = job_obj.schedule()
                if schedule_obj is not None:
                    schedule_obj(job_queue.put, v)
            except (ImportError, AttributeError) as e:
                print(e.__repr__())
            except Exception as e:
                print(e.__repr__())
        workers = []
        for i in range(0, self._worker_num):
            workers.append(Process(target=__class__._worker_main, daemon=daemon,
                                   kwargs={'worker_no': i, 'jobs_module_name': self._jobs_module,
                                           'queue': job_queue,
                                           'logger': self._logger}))
            workers[i].start()

        while 1:
            schedule.run_pending()
            time.sleep(1)

    def run(self, name: str):
        """
        执行单个job
        :return:
        """
        module_name = name + '_job'
        cls_name = underline2hump(module_name)
        try:
            job_module = __import__(self._jobs_module + '.' + module_name)
            job = getattr(getattr(job_module, module_name), cls_name)
            job(self._logger).run()
        except (ImportError, AttributeError) as e:
            print(e.__repr__())

    def test(self, name: str):
        """
        测试job是否正常
        :param name:
        :return:
        """
        module_name = name + '_job'
        cls_name = underline2hump(module_name)
        try:
            job_module = __import__(self._jobs_module + '.' + module_name)
            job = getattr(getattr(job_module, module_name), cls_name)
            if callable(job(self._logger).run):
                self._logger.info('job: ' + name + ' success')
            else:
                self._logger.error('job: ' + name + ' failed, msg: 请确认是否实现了 run 方法')
        except (ImportError, AttributeError) as e:
            self._logger.error('job: ' + name + ' failed, msg: jobs.' + module_name + ' 不存在 或 run 方法不存在')
        except Exception as e:
            self._logger.error('job: ' + name + ' failed, msg: ' + e.__repr__())
