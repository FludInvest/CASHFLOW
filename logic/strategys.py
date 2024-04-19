from tinkoff.invest import Client, OrderType, OrderDirection, CandleInterval, InstrumentStatus, PositionsResponse
from datetime import *
from dotenv import load_dotenv
from logic.get_data import *
from logic.indicators import *
from config import *
from base import *
from multiprocessing import Process
import os
import time
import asyncio



class StartLogic:
    def __init__(self,ticker,quantity,price,lot):
        super().__init__(ticker,quantity,price,lot)
    
    def start(self):
        pass

class Logic:
    def __init__(self,ticker,figi,quantity,lot):
        self.open_position = True
        self.figi = figi
        self.qty = quantity
        self.lot = lot 
        self.ticker = ticker

        self.stop_loss = 0
        self.take = 0
        self.bu = False
    
    def start(self):
        with Client(os.getenv('TINKOFF')) as client:
            try:
                self.order_buy = client.orders.post_order(
                    order_id=str(datetime.now().timestamp()),
                    figi=self.figi,
                    quantity=int(self.qty),
                    account_id=client.users.get_accounts().accounts[0].id,
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    order_type=OrderType.ORDER_TYPE_MARKET)

                self.all_buyprice = convert_money(self.order_buy.initial_order_price)
                self.buyprice = convert_money(self.order_buy.executed_order_price)

                print(self.order_buy,self.buyprice)

                while self.order_buy.execution_report_status != 1: pass

                self.stop_loss = self.buyprice * .98
                self.take = self.buyprice * 1.01

                asyncio.run(Get().change_data("INSERT INTO BUY VALUES (%s,%s,%s)",(self.ticker,self.buyprice,self.qty * self.lot,)))
                asyncio.run(Get().change_data("INSERT INTO DEALS VALUES (%s,%s,%s)",(self.ticker,self.qty * self.lot,self.buyprice,)))

                while self.open_position:
                    asyncio.sleep(5)
                    self.data_1h = (asyncio.run(get_data(shares[(shares['figi'] == self.figi)]['ticker'].values[0],60,hour)))

                    if self.take <= self.data_1h['close'].values[-1:][0] and self.bu == False:
                        self.bu = True
                        self.stop_loss = self.buyprice * 1.002
                        self.take = self.buyprice * 1.02
                    
                    if self.take <= self.data_1h['close'].values[-1:][0] and self.bu:
                        self.stop_loss = self.stop_loss * 1.01
                        self.take = self.take * 1.01

                    if self.stop_loss > self.self.data_1h['close'].values[-1:][0]:
                        self.sell()

            except Exception as error:
                print(error)

    def sell(self):  
        with Client(os.getenv('TINKOFF')) as client:
            try:
                self.order_sell = client.orders.post_order(
                                 order_type=OrderType.ORDER_TYPE_MARKET,
                                 figi=self.figi,
                                 account_id=client.users.get_accounts().accounts[0].id,
                                 direction=OrderDirection.ORDER_DIRECTION_SELL,
                                 quantity=int(self.qty))
                
                while self.order_sell.execution_report_status != 1: pass

                asyncio.run(Get().change_data("INSERT INTO SELL VALUES (%s,%s,%s,%s)",(self.ticker,self.buyprice,self.qty,self.order_sell.executed_order_price,)))
                asyncio.run(Get().change_data("DELETE FROM DEALS WHERE TICKER = (%s)",(self.ticker,)))
                self.open_position = False
                
            except Exception as errore:
                print(errore)

def creating_task(ticker,figi,quantity,lot):
    Process(target=Logic(ticker,figi,quantity,lot).start()).start()


def check_share(*args):
    with Client(os.getenv('TINKOFF')) as client:
            for i in args:
                time.sleep(1)
                try:
                    work = asyncio.run(Get().fetchone("SELECT BOT_WORK FROM ACCOUNT_INFO"))
                    if client.market_data.get_trading_status(
                        instrument_id=i).limit_order_available_flag and work == (1,):
                        
                        data_1h = (asyncio.run(get_data(shares[(shares['figi'] == i)]['ticker'].values[0],60,hour)))

                        ticker = shares[(shares['figi'] == i)]['ticker'].values[0]
                        lot = shares[(shares['figi'] == i)]['lot'].values[0]

                        if ema(data_1h,12)[-1:] > ema(data_1h,24)[-1:] > ema(data_1h,36)[-1:] and adaptive_ma(data_1h,14,6,30)[-1:] < data_1h['close'].values[-1:][0] and\
                            rsi(data_1h)[-1:].values[0] <= 50:
                            if get_qty(data_1h['close'].values[-1:][0],lot) >= 1:
                                if asyncio.run(Get().fetchone("SELECT TICKER FROM DEALS WHERE TICKER = (%s)",(shares[(shares['figi'] == i)]['ticker'].values[0],))) is None:
                                    creating_task(ticker,i,get_qty(data_1h['close'].values[-1:][0],lot),lot)
                except Exception as er:
                    pass

                    

       