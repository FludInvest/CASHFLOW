from config import *
from logic.get_data import *
from logic.indicators import *
from logic.strategys import *
from log_folder._log import *
from base import *
from discord_classes import *

from disnake.ext import commands
from discord_webhook import DiscordWebhook, DiscordEmbed
import disnake

from tinkoff.invest import Client
import asyncio
import os
from dotenv import load_dotenv
from multiprocessing import Process

bot = commands.Bot()

@bot.slash_command()
async def ready(interaction):
    work = await Get().fetchone("SELECT BOT_WORK FROM ACCOUNT_INFO")
    if work == (0,):
        await interaction.send(view=StartBot())

    elif work == (1,): 
        await interaction.send(view=StopBot())

@bot.slash_command()
async def menu(interaction):
    await interaction.send(view=Menu())
 
@bot.event
async def on_ready():
        start_log("BOT IS ON")
        load_dotenv('.env')


        while True:
            await asyncio.sleep(2)
            try:
                
                deal = DiscordWebhook(url=os.getenv('DISCORD_WEBHOOK'))
                
                if await Get().fetchone("SELECT * FROM BUY") is not None:
                    embed = DiscordEmbed(title="Buy", color="00FF00")

                    info = await Get().fetchone("SELECT * FROM BUY")

                    embed.add_embed_field(name="Ticker🎫", value=str(info[0]))
                    embed.add_embed_field(name="BuyBrice💸", value=f"{info[1]} ₽")
                    embed.add_embed_field(name="Quantity🥑", value=f"{info[2]} Shares")
                    embed.set_thumbnail(url=urls['buy'])
                    deal.add_embed(embed)

                    await Get().change_data("DELETE FROM BUY WHERE TICKER = %s",(info[0],))
                    resource = deal.execute()


                if await Get().fetchone("SELECT * FROM SELL") is not None:
                    embed = DiscordEmbed(title="Sell", color="DC143C")

                    info = await Get().fetchone("SELECT * FROM SELL")
                    profit = f"{(info[3] - info[1]) * info[2]} ₽\n{round((info[3] - info[1]) / info[1] * 100,2)}%"


                    embed.add_embed_field(name="Ticker🎫", value=str(info[0]))
                    embed.add_embed_field(name="BuyBrice💸", value=f"{info[1]} ₽")
                    embed.add_embed_field(name="Quantity🥑", value=f"{info[2]} Shares")
                    embed.add_embed_field(name="SellPrice🧾", value=f"{info[3]} ₽")
                    embed.add_embed_field(name="Profit🦾", value=profit)
                    embed.set_thumbnail(url=urls['sell'])
                    deal.add_embed(embed)

                    await Get().change_data("DELETE FROM SELL WHERE TICKER = %s",(info[0],))
                    resource = deal.execute()


                if await Get().fetchone("SELECT * FROM START") is not None:
                    embed = DiscordEmbed(title="Flow restoration", color="000080")

                    info = await Get().fetchone("SELECT * FROM START")

                    embed.add_embed_field(name="Ticker🎫", value=str(info[0]))
                    embed.add_embed_field(name="BuyBrice💸", value=f"{info[1]} ₽")
                    embed.add_embed_field(name="Quantity🥑", value=f"{info[2]} Shares")
                    embed.set_thumbnail(url=urls['flow'])
                    deal.add_embed(embed)

                    await Get().change_data("DELETE FROM START WHERE TICKER = %s",(info[0],))
                    resource = deal.execute()



            except Exception as error_code:
                 add_log(error_code)
                 
if __name__ == "__main__":
    load_dotenv('.env')

    asyncio.run(MySQLConnection().on_start())

    with Client(os.getenv("TINKOFF")) as client:
        my_shares = client.operations.get_portfolio(account_id=client.users.get_accounts().accounts[0].id)

        for i, el in enumerate(my_shares.positions):
            try:
                info = shares[(shares['figi'] == my_shares.positions[i].figi)]
                creating_task(info["ticker"].values[0],
                                my_shares.positions[i].figi,
                                my_shares.positions[i].quantity.units,
                                convert_money(my_shares.positions[i].average_position_price),
                                info['lot'].values[0])


            except Exception:
                pass

    process_1 = Process(target=check_share,args=shares['figi'].values[:int(len(shares) * .33):])
    process_2 = Process(target=check_share,args=shares['figi'].values[int(len(shares) * .33):int(len(shares) * .66):])
    process_3 = Process(target=check_share,args=shares['figi'].values[int(len(shares) * .66)::])
    
    process_1.start()
    process_2.start()
    process_3.start()
    

    bot.run(os.getenv('DISCORD'))
    

