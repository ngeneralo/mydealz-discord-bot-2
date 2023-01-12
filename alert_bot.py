from discord.ext import tasks
import discord
import json
import products

# Load credentials
with open('credentials.json','r') as file:
    creds = json.load(file)

TOKEN = creds["token"]

class AlertBot:
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents = intents)
    
    async def send_message(self,message:discord.message.Message, reponse:str):
        try:
            await message.channel.send(reponse)
        except Exception as e:
            print(e)
    
    def run(self):

        @tasks.loop(seconds=10)
        async def wait_for_product():
            pass
        
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

            if user_message == "product":
                for p in products.get_latest():
                    await self.send_message(message,str(p))
        
        self.client.run(TOKEN)


if __name__ == "__main__":
    bot = AlertBot()
    bot.run()