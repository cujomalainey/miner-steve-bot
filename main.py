from daemon.runner import DaemonRunner
from time import sleep
import tempfile

class steve_miner_bot:

    def __init__(self):
        self.stdin_path = tempfile.mkstemp()[1]
        print(self.stdin_path)
        self.stdout_path = tempfile.mkstemp()[1]
        self.stderr_path = tempfile.mkstemp()[1]
        self.pidfile_path = "/tmp/steve_miner_bot.pid"

    def run(self):
        while True:
            sleep(1)

bot = DaemonRunner(steve_miner_bot())
bot.do_action()
