from tinkoff.invest import Client
from config import *
from base import *
from get_data import *
from indicators import *
from time import sleep
from random import randint


class Logic_Start():
    def __init__(self,ticker,figi,quantity,price):

        self.ticker = ticker,
        self.figi = figi,
        self.price = price,
        self.quantity = quantity
        self.open_position = True

        async def check():
            await change_data("INSERT INTO START VALUES (%s,%s,%s)",(self.ticker[0],self.quantity,self.price[0],))
            await change_data("INSERT INTO DEALS VALUES (%s,%s,%s,%s)",(self.ticker[0],self.quantity,self.price[0],None,))

            while self.open_position:
                sleep(5)
                try: 
                    self.data_5_min = await get_data_tinkoff(shares[(shares['ticker'] == self.ticker[0]) & (shares['buy_available_flag'] == True)]['figi'].values[0],5)
                    self.data_4_h = await get_data_tinkoff(shares[(shares['ticker'] == self.ticker[0]) & (shares['buy_available_flag'] == True)]['figi'].values[0],240)
                    self.data_10_min = await get_data_aiomoex(self.ticker[0],10)
                    self.data_1_h = await get_data_aiomoex(self.ticker[0],60)
                    self.data_1_d = await get_data_aiomoex(self.ticker[0],24)

                    if self.price[0] * 0.9 >= self.data_5_min['close'].values[-1]:
                        await sell()
                    else:
                        if get_heiken_ashi(self.data_1_d)['close'].values[-1] < get_heiken_ashi(self.data_1_d)['close'].values[-2] and\
                            self.price * 1.003 < self.data_5_min['close'].values[-1]:
                            await sell()
                        else:
                            if self.price[0] * 0.98 >= self.data_5_min['close'].values[-1]:
                                await sell()
                            else:
                                if self.price * 1.002 < self.data_5_min['close'].values[-1]:
                                    await sell()


                except Exception as error_code:
                    print(error_code)

                    await change_data("INSERT INTO ERRORS VALUES (%s,%s)",(self.ticker[0],str(error_code),))
                    self.open_position = False


        async def sell():
            with Client(tokens['tinkoff']) as client:
                order_sell = client.orders.post_order(
                            order_type=OrderType.ORDER_TYPE_MARKET,
                            figi=self.figi,
                            account_id=client.users.get_accounts().accounts[0].id,
                            direction=OrderDirection.ORDER_DIRECTION_SELL,
                            quantity=self.quantity)

                while order_sell.execution_report_status != 1:
                    pass

                await change_data("INSERT INTO SELL VALUES (%s,%s,%s,%s)",(randint(1000,9999),self.ticker[0],self.price[0],self.quantity,order_sell.executed_order_price))
                await change_data("DELETE FROM DEALS WHERE TICKER = %s",(self.ticker[0],))

                await change_data("UPDATE ACCOUNTS SET PROFIT = %s WHERE ID = 0",(
                    await fetchone("SELECT PROFIT FROM ACCOUNTS WHERE ID = 0") + order_sell.executed_order_price,))
                
                await change_data("UPDATE ACCOUNTS SET QUANTITY_DEALS = %s WHERE ID = 0",(
                    await fetchone("SELECT QUANTITY_DEALS FROM ACCOUNTS WHERE ID = 0") + 1,))

                self.open_position = False


        asyncio.run(check())


Logic_Start("ROSN",1,1,1)

