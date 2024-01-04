import discord
from products import *
import json

MAIN_ALERT = 1063857337221263421

class PriceRule:
    def __init__(self,min_price = 0, max_price = 0, min_disc = 0):
        self.min_price = min_price
        self.max_price = max_price
        self.min_disc = min_disc
    
    def __repr__(self) -> str:
        min_price_str = float_to_price(self.min_price)
        max_price_str = float_to_price(self.max_price)

        return f"{min_price_str} - {max_price_str} and {self.min_disc}%"
        
def dict_to_rule(rdict:dict)->tuple[str,PriceRule]:
    role = rdict['role']
    rule = PriceRule(rdict['min_price'],rdict['max_price'],rdict['min_disc'])
    return role,rule

class ChannelClient:
    def __init__(self,channel:discord.channel.TextChannel):
        self.channel : discord.channel.TextChannel = channel
        self.price_rules : list[tuple[str,PriceRule]] = []  # (role,PriceRule)
        self.buzzwords : list[tuple[str,str]] = []  # (role,str)
        self.sent_products : list[str] = []
        self.read_from_json()

    def to_dict(self):
        rules_dict = []
        bw_dict = []
        for role,word in self.buzzwords:
            bw_dict += [{"role":role,"word":word}]
        for role,rule in self.price_rules:
            rules_dict += [{
                "role":role,
                "min_price":rule.min_price,
                "max_price":rule.max_price,
                "min_disc":rule.min_disc}]
        return {"rules":rules_dict,"buzzwords":bw_dict}
    

    def read_from_json(self):
        # load data
        with open('client_data.json','r') as file:
            data = json.load(file)
        if str(self.channel.id) not in data.keys():
            return
        rules = data[str(self.channel.id)]['rules']
        for rr in rules:
            try:
                self.price_rules += [dict_to_rule(rr)]
            except Exception as e:
                print("Error in json read ",e)
        buzzwords = data[str(self.channel.id)]['buzzwords']
        for bw in buzzwords:
            try:
                self.buzzwords += [(bw['role'],bw['word'])]
            except Exception as e:
                print("Error in json read ",e)
        
    def update_json(self):
        with open('client_data.json','r') as file:
            data = json.load(file) #load
        data[str(self.channel.id)] = self.to_dict() #update
        with open('client_data.json','w') as file:
            json.dump(data,file,indent=4)
    
    def add_rule(self, rule:PriceRule, role:str):
        self.price_rules.append((role,rule))
        self.update_json()
    
    def add_buzzword(self,buzzword:str, role:str):
        self.buzzwords.append((role,buzzword))
        self.update_json()
    
    # removes rule at index and returns it
    def pop_rule(self,index:int):
        if index < 0 or index >= len(self.price_rules):
            return
        role,rule = self.price_rules.pop(index)
        self.update_json()
        return rule
    
    # removes buzzword...
    def pop_buzzword(self,index:int):
        if index < 0 or index >= len(self.buzzwords):
            return
        role,word = self.buzzwords.pop(index)
        self.update_json()
        return word
    
    # returns string of roles if valid else returns empty string
    def product_valid(self,product:Product)->tuple[bool,str]:
        roles = set()
        valid = False

        # check if product is in sent_alerts.json
        with open('sent_alerts.json','r') as file:
            sent_alerts = json.load(file)
        if self.channel.id == MAIN_ALERT and product.product_code in sent_alerts:
            return False,''
        
        if product.product_code in self.sent_products:
            return False,''

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
    
    def add_product_to_file(self, timestamp_utc, product:Product):
        self.sent_products.append(product.product_code)
        if self.channel.id != MAIN_ALERT:
            return
        timestamp = timestamp_utc.astimezone().replace(tzinfo=None)
        product_code = product.product_code
        with open('sent_alerts.json','r') as file:
            sent_alerts = json.load(file)
        if product_code not in sent_alerts:
            sent_alerts[product_code] = {"datetime": str(timestamp),
                         "url": product.url}
        with open('sent_alerts.json','w') as file:
            json.dump(sent_alerts, file, indent=4)
        