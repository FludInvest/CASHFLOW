from base import *
from disnake.ext import commands
from disnake import TextInputStyle, ModalInteraction
from discord_webhook import DiscordWebhook, DiscordEmbed
import disnake
from dotenv import load_dotenv
from config import *
from logic.get_data import *


class Isk_Modal_Cl(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Исключение Акций",
                placeholder="Введите тикеры акций через пробел",
                custom_id="field",
                style=TextInputStyle.paragraph
            )
        ]
        super().__init__(title="🗑️Cleaning🗑️", components=components)

    async def callback(self, interaction: ModalInteraction):

        query = 0
        for el in interaction.text_values["field"].split(' '):
            if el.upper() in [x[0] for x in await Get().fetchall("SELECT * FROM EXCLUSION_LIST")]:
                query = query + 1
                await Get().change_data("DELETE FROM EXCLUSION_LIST WHERE LIST = (%s)", (el.upper(),))
        await interaction.send(f"❌Delete {query} element✅")


class Iskl_Modal(disnake.ui.Modal):

    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Exclusin Shares",
                placeholder="Enter shares name",
                custom_id="field",
                style=TextInputStyle.paragraph
            )
        ]
        super().__init__(title="➕Add➕", components=components)

    async def callback(self, interaction: ModalInteraction):
        query = 0
        for el in interaction.text_values["field"].split(' '):

            if el.upper() not in [x[0] for x in await Get().fetchall("SELECT * FROM EXCLUSION_LIST")]:
                if el.upper() in shares['ticker'].values:
                    query = query + 1
                    await Get().change_data("INSERT INTO EXCLUSION_LIST VALUES (%s) ",(el.upper(),))

        await interaction.send(f"💾Add {query} element✅")


class Add(disnake.ui.View):
    @disnake.ui.button(label="➕Add➕", style=disnake.ButtonStyle.success)
    async def add(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.message.delete()
        await interaction.response.send_modal(modal=Iskl_Modal())

    @disnake.ui.button(label="❌Delete❌", style=disnake.ButtonStyle.danger)
    async def del_one_more(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.message.delete()
        await interaction.response.send_modal(Isk_Modal_Cl())

    @disnake.ui.button(label="🛑Delete ALL🛑", style=disnake.ButtonStyle.danger)
    async def del_all(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.message.delete()
        await Get().change_data("DELETE FROM EXCLUSION_LIST")
        await interaction.send("✅ Clear ✅")


class All_off(disnake.ui.View):
    @disnake.ui.button(label="⚡Всё равно выключить⚡", style=disnake.ButtonStyle.danger)
    async def stop_btn_2(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.message.delete()

        await Get().change_data("UPDATE ACCOUNT_INFO SET BOT_WORK = True ")

        await interaction.channel.send("Бот остановлен✋")


class StartBot(disnake.ui.View):
    @disnake.ui.button(label="🆕Запустить🆕", style=disnake.ButtonStyle.success)
    async def start_btn(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.message.delete()
        await Get().change_data("UPDATE ACCOUNT_INFO SET BOT_WORK = True")
        await interaction.channel.send("Бот Запущен, да прибудет с вами прибыль📈")


class StopBot(disnake.ui.View):
    @disnake.ui.button(label="🛑Остановить🛑", style=disnake.ButtonStyle.danger)
    async def stop_btn(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.message.delete()
        if await Get().fetchone("SELECT * FROM DEALS") is None:
            await Get().change_data("UPDATE ACCOUNT_INFO SET BOT_WORK = True ")
            await interaction.channel.send("Бот остановлен✋")
        else:
            await interaction.channel.send(
                "Есть не оконченные сделки,если выключить бота он завершит последние ,но в новые входить не будет",
                view=All_off())


class Menu(disnake.ui.View):
    @disnake.ui.button(label="📖Active Deals📖", style=disnake.ButtonStyle.success)
    async def active_deal_btn(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.message.delete()
        if await Get().fetchone("SELECT * FROM DEALS") is None:
            await interaction.channel.send("❌No active trades❌")
        else:
            load_dotenv('.env')
            deal = DiscordWebhook(url=os.getenv('DISCORD_WEBHOOK'))
            embed = DiscordEmbed(title="📖Active Deals📖", color="ff00ff")

            for index, el in enumerate(await Get().fetchall("SELECT * FROM DEALS")):
                value = f"{index + 1}  Ticker : {el[0]}  Buyprice : {el[2]}  Quantity :  {el[1]}"
                embed.add_embed_field(name="", value=value, inline=False)
            deal.add_embed(embed)
            resource = deal.execute()

    @disnake.ui.button(label="❌Exclusion list❌", style=disnake.ButtonStyle.success)
    async def iskl(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.message.delete()
        if await Get().fetchone("SELECT * FROM EXCLUSION_LIST") is None:
            await interaction.channel.send("❌Empty❌", view=Add())
        else:
            load_dotenv('.env')
            deal = DiscordWebhook(url=os.getenv('DISCORD_WEBHOOK'))
            embed = DiscordEmbed(title="❌Exclusion list❌", color="DC143C")
            value = ''
            for i, e in enumerate(await Get().fetchall("SELECT * FROM EXCLUSION_LIST")):
                value = f"{value} {e[0]}"
            embed.add_embed_field(name='', value=value, inline=False)
            embed.set_thumbnail(url=urls['exclusion'])

            deal.add_embed(embed)
            resource = deal.execute()
            await interaction.channel.send(view=Add())

    @disnake.ui.button(label="📝Statistic✍️", style=disnake.ButtonStyle.success)
    async def stat(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await interaction.message.delete()
        load_dotenv('.env')
        deal = DiscordWebhook(url=os.getenv('DISCORD_WEBHOOK'))
        embed = DiscordEmbed(title="Statistic", color="FF0000")

        for index, el in enumerate(await Get().fetchall("SELECT * FROM ACCOUNT_INFO")):

            embed.add_embed_field(name="💰Доходность💰", value=f"{round(el[2],3)}", inline=False)
            embed.add_embed_field(name="➕Кол-во сделок➕ ", value=f"{el[1]}", inline=False)
            embed.set_thumbnail(url=urls['stat'])

        deal.add_embed(embed)
        resource = deal.execute()

