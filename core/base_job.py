from typing import Callable, Any, Tuple, Dict, Union
import schedule
import logging
import abc


class BaseJob(object):
    """
    任务基类
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    @abc.abstractmethod
    def run(self):
        """
        need to be implemented
        :return:
        """
        return

    def schedule(self) -> Union[None, Callable[[schedule.Job, Any, Tuple[Any, ...], Dict[str, Any]], schedule.Job]]:
        """
        返回计划执行时间
        :return:
        """
        return schedule.every(60).seconds.do

    @property
    def logger(self):
        return self._logger
