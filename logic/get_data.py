from tinkoff.invest import Client, OrderType, OrderDirection, CandleInterval, InstrumentStatus, PositionsResponse
from tinkoff.invest.services import InstrumentsService, MarketDataService
from tinkoff.invest import Client
from indicators import *

import aiohttp
import asyncio
import pandas
import aiomoex
import asyncio
import pandas

from config import *

from datetime import *


with Client(tokens['tinkoff']) as client:
    shares = pandas.DataFrame(
        client.instruments.shares(
            instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments,
        columns=['currency', 'lot', 'figi', 'ticker', 'buy_available_flag',
                 'for_qual_investor_flag', 'api_trade_available_flag'])

    shares_auto = shares[
        (shares['for_qual_investor_flag'] == False) & (shares['currency'] == 'rub') & (
                shares['buy_available_flag'] == True) & (shares['api_trade_available_flag'] == True)]

    shares_signal = shares[
        (shares['for_qual_investor_flag'] == False) & (shares['currency'] == 'rub') & (
                shares['buy_available_flag'] == True) & (shares['api_trade_available_flag'] == False)]

async def get_threads():
    shares_check_for_threads = client.operations.get_portfolio(account_id=client.users.get_accounts().accounts[0].id)
    for i, el in enumerate(shares_check_for_threads.positions):
        try:
            info = shares[(shares_auto['figi'] == shares_check_for_threads.positions[i].figi)]

            Logic_Start(info["ticker"].values[0],
                        shares_check_for_threads.positions[i].figi,
                        shares_check_for_threads.positions[i].quantity.units,
                        convert_money(shares_check_for_threads.positions[i].average_position_price),info['lot'].values[0])

        except Exception as er:
            print(er)

async def get_data_aiomoex(ticker,timeframe):
    async with aiohttp.ClientSession() as session:
        if timeframe == 10:
            frame = pandas.DataFrame(await aiomoex.get_board_candles(
                session = session,
                security = ticker,
                interval = timeframe,
                start = (datetime.now() - timedelta(weeks=2)).strftime("%Y%m%d")))
            
        else:

            if timeframe == 60:
                frame = pandas.DataFrame(await aiomoex.get_board_candles(
                    session = session,
                    security = ticker,
                    interval = timeframe,
                    start = (datetime.now() - timedelta(weeks=5)).strftime("%Y%m%d")))
            else:
        
                if timeframe == 24:
                    frame = pandas.DataFrame(await aiomoex.get_board_candles(
                        session = session,
                        security = ticker,
                        interval = timeframe,
                        start = (datetime.now() - timedelta(weeks=70)).strftime("%Y%m%d")))
        try:
            frame = frame.set_index("begin")
            frame.index = pandas.to_datetime(frame.index,format="%Y-%m-%d %H:%M:%S")
        except:
            return None

        return frame


async def get_data_tinkoff(figi,timeframe):
    async def create_frame(candles):
        return pandas.DataFrame([{
            'time':candle.time,
            'volume':candle.volume,
            'open':convert_money(candle.open),
            'low':convert_money(candle.low),
            'high':convert_money(candle.high),
            'close':convert_money(candle.close)
        } for candle in candles])


    with Client(tokens['tinkoff']) as client:
        if timeframe == 5:
            order = client.market_data.get_candles(
                figi = figi,
                from_ = datetime.now() - timedelta(days=1),
                to = datetime.now(),
                interval = CandleInterval.CANDLE_INTERVAL_5_MIN
            )
        else:
            if timeframe == 240:
                order = client.market_data.get_candles(
                    figi = figi,
                    from_ = datetime.now() - timedelta(days=1),
                    to = datetime.now(),
                    interval = CandleInterval.CANDLE_INTERVAL_4_HOUR
                )
        return await create_frame(order.candles)



    



