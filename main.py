from daemon.runner import DaemonRunner
from mcstatus import MinecraftServer
from time import sleep
from concurrent.futures import ThreadPoolExecutor

import os
import tempfile
import discord
import asyncio
import random

WELCOME_MSG = "Hello, I am miner Steve, I will keep tabs on your shifts and keep track of any mine collapses.\nBest luck hunting for diamonds."
SERVER_DOWN = "<@{}> there has been a mine collapse! (Server is down)"
SERVER_UP = "Mine collapse has cleared, the mine is open! (Serve is up)"

LOGIN_MSG = [
    "Fire up the drill! {} has begun mining.",
    "{} has punched the clock, time to start prospecting.",
    "Bring in the canary, {} has started hunting for coal.",
    "Light your torches, {} is entering the mines.",
    "Grab your swords, {} has started hunting zombies.",
    "Better hurry, {} is looking for diamonds.",
    "{} is on a quest, the nether awaits!",
]

async def in_thread(func):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func)

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        self.channel = self.get_channel(int(os.environ['DISCORD_CHANNEL'])) # channel ID goes here
        self.mine_manager = os.environ["MINE_MANAGER"]
        self.mc_server = MinecraftServer(os.environ['MC_SERVER'])
        # await self.channel.send(WELCOME_MSG)
        activity = discord.CustomActivity("Miners: {}".format(0))
        await self.change_presence(status=discord.Status.idle, activity=activity)
        self.mc_is_up = True
        self.user_count = 0
        self.current_players = set()
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def my_background_task(self):
        await self.wait_until_ready()
        while not self.is_closed():
            await self.check_server_up()
            if self.is_up:
                await self.check_user_count()
                await self.check_shifts()
            await asyncio.sleep(15) # task runs every 15 seconds

    async def check_server_up(self):
        change = False
        is_up = False
        # for i in range(0,3):
        try:
            ping = self.mc_server.ping()
            is_up = True
        except:
            pass
        change = self.mc_is_up != is_up
        if change:
            if is_up:
                # server came online
                await self.channel.send(SERVER_UP)
            else:
                await self.channel.send(SERVER_DOWN.format(self.mine_manager))
        self.is_up = is_up


    async def check_user_count(self):
        try:
            status = self.mc_server.status()
        except:
            return
        count = status.players.online
        change = count != self.user_count

        if change:
            status = discord.Status.online
            if count == 0:
                status = discord.Status.idle
            activity = discord.CustomActivity("Miners {}".format(count))
            await self.change_presence(status=status, activity=activity)

    async def check_shifts(self):
        try:
            query = self.mc_server.query()
        except:
            return
        current_players = set(query.players.names)
        diff = current_players - self.current_players
        self.current_players = current_players
        if len(diff) > 0:
            for p in diff:
                await self.channel.send(random.choice(LOGIN_MSG).format(p))


class steve_miner_bot:

    def __init__(self):
        self.stdin_path = tempfile.mkstemp()[1]
        self.stdout_path = tempfile.mkstemp()[1]
        self.stderr_path = tempfile.mkstemp()[1]
        self.pidfile_path = "/tmp/steve_miner_bot.pid"
        self.pidfile_timeout = 15

    def run(self):
        client = MyClient()
        client.run(os.environ['DISCORD_TOKEN'])

bot = DaemonRunner(steve_miner_bot())
bot.do_action()

# bot = steve_miner_bot()
# bot.run()


