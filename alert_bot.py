from discord.ext import tasks
from products import Product,get_latest
from channel_client import ChannelClient, PriceRule
import discord
import json
import time


# Load credentials
with open('credentials.json','r') as file:
    creds = json.load(file)

TOKEN = creds["token"]


class AlertBot:
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents = intents)
        self.channel_clients:dict[str,ChannelClient] = {}

    async def send_message(self,channel:discord.channel.TextChannel, reponse:str):
        try:
            await channel.send(reponse)
        except Exception as e:
            print(e)
    
    async def handle_bot_message(self,message:discord.message.Message):
        user_channel= message.channel
        cmd = str(message.content).split()
        while len(cmd) < 7:
            cmd.append('#')
        
        # starts bot in channel 
        if cmd[1] == "start":
            if user_channel.id not in self.channel_clients:
                new_client = ChannelClient(user_channel)
                self.channel_clients[user_channel.id] = new_client
                print(f"{user_channel} add to client list.")
                await self.send_message(user_channel,"BOT START\n*There are no rules for this bot yet.*")
        
        if user_channel.id not in self.channel_clients:
            return

        # since here, bot must be started in channel
        channel_client = self.channel_clients[user_channel.id]
        if cmd[1] == "stop":
            self.channel_clients.pop(user_channel.id)
            print(f"{user_channel} deleted from client list.")
        
        if cmd[1] == "rules":
            msg = "The price rules are:\n"
            for i,v in enumerate(channel_client.price_rules,start=1):
                role,rule = v
                msg += f"{i}. {rule} Role: {role}\n"
            await self.send_message(user_channel,msg)
        
        if cmd[1] == "buzzwords":
            msg = "The buzzwords are:\n"
            for i,v in enumerate(channel_client.buzzwords,start=1):
                role,word = v
                msg += f"{i}. {word} Role: {role}\n"
            await self.send_message(user_channel,msg)
        
        if cmd[1] == "add" and cmd[2] == "rule":
            try:
                min_price, max_price = float(cmd[3]), float(cmd[4])
                min_disc = int(cmd[5])
                role = cmd[6]
                channel_client.add_rule(PriceRule(min_price,max_price,min_disc),role)
                print(f"New rule added. ({user_channel})")
            except:
                await self.send_message(user_channel,"*Invalid format*\n"+
                "bot add rule <min price> <max price> <min discount> <role id>")
        
        if cmd[1] == "add" and cmd[2] == "buzzword":
            word = cmd[3]
            role = cmd[4]
            channel_client.add_buzzword(word,role)
            print(f"New buzzword added. ({user_channel})")
    

    def run(self):

        @tasks.loop(seconds=10)
        async def alert_loop():
            latest = get_latest()
            for prod in latest:
                for cc in self.channel_clients.values():
                    valid,role = cc.product_valid(prod)
                    if not valid: continue
                    msg = f"{role}\n{prod}"
                    await self.send_message(cc.channel,msg)
                    print(f"Sent {prod.name[:20]} to {cc.channel}")
                    cc.sended_urls.append(prod.url)
                time.sleep(1)
        
        @self.client.event
        async def on_ready():
            print(f"{self.client.user} is running.")
            alert_loop.start()
        
        @self.client.event
        async def on_message(message: discord.message.Message):
            if message.author == self.client.user:
                return

            username = str(message.author)
            user_message = str(message.content)
            channel = str(message.channel.id)
            print(f"{username} said: '{user_message}' ({channel})")

            if user_message.lower().startswith("bot "):
                await self.handle_bot_message(message)
            
        
        self.client.run(TOKEN)


if __name__ == "__main__":
    bot = AlertBot()
    bot.run()