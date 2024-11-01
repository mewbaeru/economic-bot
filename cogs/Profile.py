from disnake import Option
from disnake.ext import commands
from easy_pil import Editor, Canvas, Font, load_image_async

from database.requests import get_balance, get_user_voice_activity_data, get_clan_membership, get_count_messages, get_marry, get_info_marriage
from modules import *

guild_id = Utils.get_guild_id()

# font
font_50 = Font('./assets/profile/font/avenirnext.ttf', size=50)
font_70_bold = Font('./assets/profile/font/avenir-next-bold.ttf', size=70)

class Profile(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    async def generate_profile(self, member):
        canvas = Canvas((1920, 1080))
        editor = Editor(canvas)

        self.background = Editor("./assets/profile/default_profile.png")

        editor.paste(self.background.image, (0, 0))

        # member info
        name = member.display_name
        member_name = (name[:18] + '...') if len(name) > 10 else name
        editor.text((1670, 390), member_name, color="white", font=font_50, align="center")

        avatar = await load_image_async(str(member.display_avatar.url))
        avatar = Editor(avatar).resize((243, 243)).circle_image()
        editor.paste(avatar.image, (1543, 108))

        money = await get_balance(member.id)
        formatted_money = "{:,}".format(money).replace(',', ' ')
        editor.text((347, 530), str(formatted_money), color="white", font=font_70_bold, align="left")

        online = await get_user_voice_activity_data(member.id)
        hours = online[3]
        minutes = online[2]
        formatted_online = f"{hours} ч {round(minutes)} м"
        editor.text((970, 530), formatted_online, color="white", font=font_70_bold, align="left")

        clan = await get_clan_membership(member.id)
        if clan:
            # the logic of adding clan information from the clan bot database
            formatted_clan = ' '
        else:
            formatted_clan = 'X'
        editor.text((347, 770), formatted_clan, color="white", font=font_70_bold, align="left")

        messages = await get_count_messages(member.id)
        formatted_messages = "{:,}".format(messages).replace(',', ' ')
        editor.text((970, 770), str(formatted_messages), color='white', font=font_70_bold, align="left")

        marry = await get_marry(member.id)
        if marry:
            info_marriage = await get_info_marriage(member.id)
            partner_1 = info_marriage[0]
            partner_2 = info_marriage[1]

            partner_id = partner_1 if partner_1 != member.id else partner_2
            partner_user = await self.client.fetch_user(partner_id)

            partner_avatar = await load_image_async(str(partner_user.display_avatar.url))
            partner_avatar = Editor(partner_avatar).resize((160, 160)).circle_image()
            editor.paste(partner_avatar.image, (40, 830))

        return editor
    
    # profile
    @commands.slash_command(name='profile', description='Профиль пользователя', guild_ids=[guild_id])
    async def profile(self, interaction, member: disnake.Member = commands.Param(default=None, description='Выберите пользователя для взаимодействия')):
        logger.debug('/profile - start')
        if member is None:
            member = interaction.author
        elif member.bot:
            embed = set_invalid_user(interaction, 'Профиль пользователя', 'бота')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        profile = await self.generate_profile(member)
        file = disnake.File(fp=profile.image_bytes, filename='./assets/profile/default_profile.png')
        await interaction.followup.send(file=file)
            
def setup(client):
    client.add_cog(Profile(client))