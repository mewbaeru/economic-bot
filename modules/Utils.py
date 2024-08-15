import json

class Utils:
    def __init__(self):
        self.MessageCount = {}
        self.ActiveGames = []

    def get_guild_id():
        with open('./assets/settings.json', 'r', encoding='utf-8') as settings:
            data = json.load(settings)
            
            return data.get('guild_id')
    
    # counter messages
    def write_message(self, author):
        if author in self.MessageCount:
            self.MessageCount[author] += 1
        else:
            self.MessageCount[author] = 1
    
    def get_messages(self):
        messages = self.MessageCount
        self.MessageCount = {}

        return messages
    
    # info about personal roles
    def get_personal_roles():
        with open('./assets/settings.json', 'r', encoding='utf-8') as settings:
            data = json.load(settings)
            settings_roles = data.get('roles')
            settings_prices = data.get('prices')
            return settings_roles, settings_prices
    
    # info about channels
    def get_channels():
        with open('./assets/settings.json', 'r', encoding='utf-8') as settings:
            data = json.load(settings)
            settings_channels = data.get('channels')
            return settings_channels
        
    # server games
    def start_game(self, member_id):
        self.ActiveGames.append(member_id)
    
    def stop_game(self, member_id):
        self.ActiveGames.remove(member_id)
    
    def is_active_game(self, member_id):
        return member_id in self.ActiveGames