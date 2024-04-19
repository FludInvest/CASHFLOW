import aiomoex
import aiohttp
import asyncio
import pandas
import os
from config import *

from tinkoff.invest import Client, InstrumentStatus
from dotenv import load_dotenv

load_dotenv('.env')
with Client(os.getenv('TINKOFF')) as client:
    shares = pandas.DataFrame(
        client.instruments.shares(
            instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments,
        columns=['currency', 'ticker', 'buy_available_flag',
                 'for_qual_investor_flag', 'api_trade_available_flag','lot','figi'])

    shares = shares[
        (shares['for_qual_investor_flag'] == False) & (shares['currency'] == 'rub') & (
                shares['buy_available_flag'] == True) & (shares['api_trade_available_flag'] == True)]

async def get_data(ticker,period,status = None):
    async with aiohttp.ClientSession() as session:
        data = await aiomoex.get_board_candles(
            session = session,
            security = ticker,
            interval = period,
            start=status)
        
        return pandas.DataFrame(data)
        
        