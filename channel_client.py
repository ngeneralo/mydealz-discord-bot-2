import discord
from products import *

class PriceRule:
    def __init__(self,min_price = 0, max_price = 0, min_disc = 0):
        self.min_price = min_price
        self.max_price = max_price
        self.min_disc = min_disc
    
    def __repr__(self) -> str:
        min_price_str = float_to_price(self.min_price)
        max_price_str = float_to_price(self.max_price)

        return f"{min_price_str} - {max_price_str} and {self.min_disc}%"
        

class ChannelClient:
    def __init__(self,channel:discord.channel.TextChannel):
        self.channel : discord.channel.TextChannel = channel
        self.price_rules : list[tuple[str,PriceRule]] = []  # (role,PriceRule)
        self.buzzwords : list[tuple[str,str]] = []  # (role,str)
        self.sended_urls : list[str] = []
    
    def add_rule(self, rule:PriceRule, role:str):
        self.price_rules.append((role,rule))
    
    def add_buzzword(self,buzzword:str, role:str):
        self.buzzwords.append((role,buzzword))
    
    # returns string of roles if valid else returns empty string
    def product_valid(self,product:Product)->tuple[bool,str]:
        roles = set()
        valid = False

        if product.url in self.sended_urls:
            return False,""

        for role,rule in self.price_rules:
            price_valid = (product.old_price >= rule.min_price) and (product.old_price <= rule.max_price)
            disc_valid = (product.discount >= rule.min_disc)
            if price_valid and disc_valid:
                valid |= True
                roles.add(role)
        for role,word in self.buzzwords:
            if word.lower() in product.name.lower():
                valid |= True
                roles.add(role)
        
        return valid,' '.join(roles)