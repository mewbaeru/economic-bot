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

            cost_role_create = settings_prices.get("role_create")
            cost_role_change_name = settings_prices.get("role_change_name")
            cost_role_change_color = settings_prices.get("role_change_color")

            return settings_roles, cost_role_create, cost_role_change_name, cost_role_change_color
    
    # info about additional role
    def get_cost_additional_role():
        with open('./assets/settings.json', 'r', encoding='utf-8') as settings:
            data = json.load(settings)

            settings_roles = data.get('roles')
            settings_prices = data.get('prices')

            additional_role_id = settings_roles.get("role_of_sending_images")
            cost_additional_role = settings_prices.get("add_role_of_sending_images")

            return additional_role_id, cost_additional_role
        
    # server games
    def start_game(self, member_id):
        self.ActiveGames.append(member_id)
    
    def stop_game(self, member_id):
        self.ActiveGames.remove(member_id)
    
    def is_active_game(self, member_id):
        return member_id in self.ActiveGames