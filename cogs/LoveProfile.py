from disnake.ext import commands, tasks
from easy_pil import Editor, Canvas, Font, load_image_async

from database.requests import get_marry, get_info_marriage, get_all_marriages, get_time_to_pay_love_room, get_balance_love_room, update_time_to_pay_love_room, take_money_love_room, divorce_marriage
from modules import *

guild_id = Utils.get_guild_id()

# font
font_50 = Font('./assets/profile/font/avenirnext.ttf', size=50)
font_70_bold = Font('./assets/profile/font/avenir-next-bold.ttf', size=70)

# get role data from settings
try: 
    settings_roles, settings_prices = Utils.get_personal_roles()
except Exception:
    logger.error('failed to load settings')

class LoveProfile(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.monthly_payment.start()

    async def generate_love_profile(self, member, marriage_data, love_room_data):
        canvas = Canvas((1920, 1080))
        editor = Editor(canvas)

        self.background = Editor("./assets/profile/love_profile.png")

        editor.paste(self.background.image, (0, 0))

        # member info
        name = member.display_name
        member_name = (name[:18] + '...') if len(name) > 10 else name
        editor.text((1670, 390), member_name, color="white", font=font_50, align="center")

        avatar = await load_image_async(str(member.display_avatar.url))
        avatar = Editor(avatar).resize((243, 243)).circle_image()
        editor.paste(avatar.image, (1543, 108))
        
        # love profile info
        partner_1_user = await self.client.fetch_user(marriage_data[0])
        partner_2_user = await self.client.fetch_user(marriage_data[1])
        partner_1_avatar = await load_image_async(str(partner_1_user.display_avatar.url))
        partner_2_avatar = await load_image_async(str(partner_2_user.display_avatar.url))
        partner_1_avatar = Editor(partner_1_avatar).resize((243, 243)).circle_image()
        partner_2_avatar = Editor(partner_2_avatar).resize((243, 243)).circle_image()
        editor.paste(partner_1_avatar.image, (935, 192))
        editor.paste(partner_2_avatar.image, (407, 192))

        money = marriage_data[2]
        formatted_money = "{:,}".format(money).replace(',', ' ')
        editor.text((347, 725), str(formatted_money), color="white", font=font_70_bold, align="left")

        hours = love_room_data['total_hours']
        minutes = love_room_data['total_minutes']
        formatted_online = f"{hours} ч {round(minutes)} м"
        editor.text((950, 725), formatted_online, color="white", font=font_70_bold, align="left")

        return editor
    
    # love profile
    @commands.slash_command(name='lprofile', description='Любовный профиль пользователя', guild_ids=[guild_id])
    async def profile(self, interaction, member: disnake.Member = commands.Param(default=None, description='Выберите пользователя для взаимодействия')):
        logger.debug('/lprofile - start')
        if member is None:
            member = interaction.author
        elif member.bot:
            embed = set_invalid_user(interaction, 'Любовный профиль пользователя', 'бота')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()

        marry = await get_marry(member.id)
        if marry:
            marriage_data = await get_info_marriage(member.id)
            love_room_data = json.loads(marriage_data[4])

            lprofile = await self.generate_love_profile(member, marriage_data, love_room_data)
            file = disnake.File(fp=lprofile.image_bytes, filename='./assets/profile/love_profile.png')
            if interaction.author == member: 
                await interaction.followup.send(file=file, view=LoveProfileView(interaction, member, marriage_data, love_room_data, settings_roles))
            else:
                await interaction.followup.send(file=file, view=View())
        else:
            embed = set_error_marry(interaction, member)
            await interaction.followup.send(embed=embed)
            return
    
    @tasks.loop(hours=24)
    async def monthly_payment(self):
        marriages = await get_all_marriages()
        if marriages:
            for marriage_id in marriages:
                time_to_pay = await get_time_to_pay_love_room(marriage_id)
                if time_to_pay and datetime.now() >= datetime.fromtimestamp(time_to_pay):
                    if await get_balance_love_room(marriage_id) >= settings_prices.get('marry_create'):
                        await update_time_to_pay_love_room(marriage_id)
                        await take_money_love_room(marriage_id, settings_prices.get('marry_create'))

                        logger.info(f'/payment love room - index: {marriage_id}')
                    else:
                        await divorce_marriage(marriage_id)
                        logger.info(f'/payment love room - delete love room - index: {marriage_id}')
        else:
            logger.info(f'/payment love room - no love rooms')

def setup(client):
    client.add_cog(LoveProfile(client))