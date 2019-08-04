# -*-coding:utf-8-*-
from werobot.robot import BaseRoBot
from werobot.utils import (
    cached_property
)

from .wxclient import WxClient


class WeRoBot(BaseRoBot):
    @cached_property
    def client(self):
        return WxClient(self.config)


WeRoBot.message_types.append('file')
