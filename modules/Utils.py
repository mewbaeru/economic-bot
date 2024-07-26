import json

class Utils:
    def __init__(self):
        self.MessageCount = {}

    def get_guild_id(self):
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