from kivy.properties import ObjectProperty

from fred_client import FredUsbClient

from rcp.components.appsettings import config
from rcp.dispatchers.base_board import BaseBoard

from kivy.logger import Logger
log = Logger.getChild(__name__)


class TCL125Board(BaseBoard):
    client = ObjectProperty(None, allownone=True)
    device = ObjectProperty(None, allownone=True)

    def __init__(self, formats, offset_provider, **kv):
        super().__init__(formats, offset_provider, 3, **kv)

        vid = config.getdefault("device", "vid", 0x2E8A)
        pid = int(config.getdefault("device", "pid", 0x000A))

        self.client = FredUsbClient(vid, pid)
        self.client.enable_polling(period_ms=25)
        self.device = {
            "scales": [
                {
                    "syncEnable": False
                },
                {
                    "syncEnable": False
                },
                {
                    "syncEnable": False
                },
            ]
        }
        self.connected = True

    def update(self, *args):
        # client.refresh() -> 
        # {'x_mm': -5.96, 'z_mm': 1.3, 'spindle_rpm': 1870, 'x_counts': -298, 'z_counts': 130, 'tick': 3430, 'flags': 1}
        try:
            v = self.client.refresh()
            log.debug(v)
            self.fast_data_values = {
                "scaleCurrent": [
                    v["spindle_rpm"],
                    v["x_counts"],
                    v["z_counts"],
                ],
                "scaleSpeed": [
                    0,
                    0,
                    0,
                ],
                "servoMode": 0,
                "cycles": 0,
                "servoCurrent": 0,
                "servoDesired": 0,
                "servoEnable": 0,
                "servoSpeed": 0,
                "stepsToGo": 0,
                "executionInterval": 0,
            }
        except Exception as e:
            self.task_update.timeout = 1.0
            self.update_tick = (self.update_tick + 1) % 100
            return
        
        self.update_tick = (self.update_tick + 1) % 100
