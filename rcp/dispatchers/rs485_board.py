import os
from pathlib import Path

from kivy.properties import ObjectProperty

from rcp.components.appsettings import config
from rcp.dispatchers.base_board import BaseBoard
from rcp.utils.communication import ConnectionManager

from kivy.logger import Logger

from rcp.utils.devices import SCALES_COUNT
log = Logger.getChild(__name__)


class RS485Board(BaseBoard):
    device = ObjectProperty(None, allownone=True)

    def __init__(self, formats, offset_provider, **kv):
        super().__init__(formats, offset_provider, SCALES_COUNT, **kv)

        serial_port = config.getdefault("device", "serial_port", "/dev/serial0")
        baudrate = int(config.getdefault("device", "baudrate", 115200))
        address = int(config.getdefault("device", "address", 17))

        self.connection_manager = ConnectionManager(
            serial_device=serial_port,
            baudrate=baudrate,
            address=address,
        )
        self.device = self.connection_manager['Global']
        self.connection_manager.connect()

    def update(self, *args):
        if self.connection_manager.device is None:
            self.connection_manager.connect()

        if self.connection_manager.device is None:
            self.connected = False
            self.task_update.timeout = 2.0
            self.update_tick = (self.update_tick + 1) % 100
            return

        try:
            self.fast_data_values = self.device['fastData'].refresh()
        except Exception as e:
            self.connection_manager._log_error_once(str(e))
            self.connection_manager.connected = False
            self.connected = False
            self.task_update.timeout = 1.0
            self.update_tick = (self.update_tick + 1) % 100
            return

        was_disconnected = not self.connected
        self.connection_manager.connected = True
        self.connected = True

        if was_disconnected:
            self.task_update.timeout = 1.0 / 30

        self.update_tick = (self.update_tick + 1) % 100
