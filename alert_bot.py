from discord.ext import tasks
from products import Product,get_latest
from channel_client import ChannelClient
import discord
import json


# Load credentials
with open('credentials.json','r') as file:
    creds = json.load(file)

TOKEN = creds["token"]


class AlertBot:
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents = intents)
        self.channel_clients:list[ChannelClient] = []
    
    def get_channels(self) -> list[discord.channel.TextChannel]:
        return list(map(lambda x: x.channel,self.channel_clients))

    async def send_message(self,message:discord.message.Message, reponse:str):
        try:
            await message.channel.send(reponse)
        except Exception as e:
            print(e)
    
    async def handle_bot_message(self,message:discord.message.Message):
        cmd = str(message.content.lower()).split()
        
        if cmd[1] == "start":
            if message.channel not in self.get_channels():
                new_client = ChannelClient(message.channel)
                self.channel_clients.append(new_client)
                print(f"{message.channel} add to client list.")
        
        if cmd[1] == "stop":
            for client in self.channel_clients:
                if client.channel == message.channel:
                    client.is_active = False
                    print(f"{client.channel} is inactive now.")
    

    def run(self):

        @tasks.loop(seconds=10)
        async def alert_loop():pass
        
        @self.client.event
        async def on_ready():
            print(f"{self.client.user} is running.")
        
        @self.client.event
        async def on_message(message: discord.message.Message):
            if message.author == self.client.user:
                return

            username = str(message.author)
            user_message = str(message.content)
            channel = str(message.channel)
            print(f"{username} said: '{user_message}' ({channel})")

            if user_message.lower().startswith("bot "):
                await self.handle_bot_message(message)
            
        
        self.client.run(TOKEN)


if __name__ == "__main__":
    bot = AlertBot()
    bot.run()