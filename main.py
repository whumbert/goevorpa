from core.artifact_manager import ArtifactManager
from core.updater import Updater
from automations.solutionerp.common.data import Data
from modules.utils.general.env import DotEnv
from modules.utils.general.envupdate import EnvUpdate
from core.api import Api
from time import sleep
from json import loads
from core.worker import worker

# class Main:
#     def __init__(self):
#         self.api = Api()
#
#     def _main(self, searchtimeout = 0):
#         self.api.search_update()
#
#         with EnvUpdate():
#             try:
#                 search_timeout = int(DotEnv().get('SEARCH_TIMEOUT'))
#             except:
#                 self.api.search_update()
#                 search_timeout = int(DotEnv().get('SEARCH_TIMEOUT'))
#
#             response = self.api.get_task("/IniciarTarefa").json()["content"]
#
#             if not response:
#                 print(f"Nenhuma Task de automação foi encontrada. Tentando novamente em {search_timeout} segundos...\n")
#                 sleep(searchtimeout  if searchtimeout else search_timeout)
#             else:
#                 response = loads(response)[0]
#
#                 _guid = response["RPA_GUID"]
#                 _use_case = response["RPA_SOURCE"]
#                 _data = loads(response["RPA_PARAMS"])
#                 _system = DotEnv().get('APPLICATION')
#
#                 _data = Data.from_raw(_data)
#
#
#
#                 result, msg = worker(_guid, _system, _use_case, _data)
#
#                 log_b64 = ''
#                 screenshot_b64 = ''
#
#                 if not result:
#                     am = ArtifactManager()
#
#                     log_b64 = am.latest_log(_use_case)
#                     screenshot_b64 = am.latest_screenshot()
#
#                 self.api.finish_task(
#                     "/FinalizarTarefa",
#                     msg,
#                     "00" if result else "01",
#                     _guid,
#                     log_b64,
#                     screenshot_b64
#                 )
#
#     def test(self):
#         self._main(1)
#
#     def start(self):
#         while True:
#             self._main(1)
#
#
# if __name__ == '__main__':
#     if DotEnv().get('ENV') != '':
#         Updater.bootstrap_automations()
#
#     start()

class Main:
    def __init__(self):
        self.api = Api()

    def _main(self, searchtimeout = '0'):
        self.api.search_update()

        with EnvUpdate():
            search_timeout = int(DotEnv().get('SEARCH_TIMEOUT'))
            response = self.api.get_task("/IniciarTarefa").json()["content"]

            if not response:
                print(f"Nenhuma Task de automação foi encontrada. Tentando novamente em {search_timeout} segundos...\n")
                sleep(int(searchtimeout)  if int(searchtimeout) else search_timeout)
            else:

                response = loads(response)[0]

                _guid = response["RPA_GUID"]
                _use_case = response["RPA_SOURCE"]
                _data = loads(response["RPA_PARAMS"])
                _system = DotEnv().get('APPLICATION')

                result, msg = worker(_guid, _system, _use_case, _data)

                log_b64 = ''
                screenshot_b64 = ''

                if not result:
                    am = ArtifactManager()

                    log_b64 = am.latest_log(_use_case)
                    screenshot_b64 = am.latest_screenshot()

                self.api.finish_task(
                    "/FinalizarTarefa",
                    msg,
                    "00" if result else "01",
                    _guid,
                    log_b64,
                    screenshot_b64
                )

    def test(self):
        self._main(1)

    def start(self):
        while True:
            self._main()

def start():
    m = Main()
    m.start()

def test():
    m = Main()
    m.test()


if __name__ == '__main__':
    if DotEnv().get('ENV') != '':
        Updater.bootstrap_automations()

    start()


