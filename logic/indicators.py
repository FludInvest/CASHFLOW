import pandas
import ta.trend,ta.momentum
from tinkoff.invest import Client
from dotenv import load_dotenv
import os

def convert_money(num):
    return num.units + num.nano / 1e9

def convert_money_for_qty(units, nano):
    return units + nano / 1e9

def reconvert_money(num):
    return int(num), int((num - int(num)) * 1e9)

def HeikenAshi(candles: pandas.DataFrame) -> pandas.DataFrame:
    heikin_ashi = pandas.DataFrame(index=candles.index.values, columns=['open', 'high', 'low', 'close'])
    
    heikin_ashi['close'] = (candles['open'] + candles['high'] + candles['low'] + candles['close']) / 4
    
    for i in range(len(candles)):
        if i == 0:
            heikin_ashi.iat[0, 0] = candles['open'].iloc[0]
        else:
            heikin_ashi.iat[i, 0] = (heikin_ashi.iat[i-1, 0] + heikin_ashi.iat[i-1, 3]) / 2
        
    heikin_ashi['high'] = heikin_ashi.loc[:, ['open', 'close']].join(candles['high']).max(axis=1)
    
    heikin_ashi['low'] = heikin_ashi.loc[:, ['open', 'close']].join(candles['low']).min(axis=1)
    
    return heikin_ashi

def ema(candles: pandas.DataFrame , period) -> pandas.DataFrame:
    return ta.trend.ema_indicator(candles['close'],window=period).values

def adaptive_ma(candles: pandas.DataFrame , period,fast,slow) -> pandas.DataFrame:
    return ta.momentum.kama(candles['close'],window=period,pow1=fast,pow2=slow,fillna=True).values

def get_qty(price, lot):

    try:
        load_dotenv('.env')
        with Client(os.getenv("TINKOFF")) as client:
            balance = client.operations.get_portfolio(
                    account_id=client.users.get_accounts().accounts[0].id)
            all_shares = convert_money_for_qty(balance.total_amount_portfolio.units,
                                                balance.total_amount_portfolio.nano)

            curr = convert_money_for_qty(balance.total_amount_currencies.units,
                                            balance.total_amount_currencies.nano)
            price = price * lot
            qty_lots = int(curr / price)


            if qty_lots < 1:
                return 0
            else:
                if all_shares < 5000:
                    return int(curr / price)
                else:
                    if 5000 < all_shares < 10000 and curr > all_shares * 0.3 > price:
                        return int(all_shares * 0.3 / price)
                    else:
                        if 10000 < all_shares < 20000 and curr > all_shares * 0.25 > price:
                            return int(all_shares * 0.25 / price)
                        else:
                            if 20000 < all_shares < 40000 and curr > all_shares * 0.2 > price:
                                return int(all_shares * 0.2 / price)
                            else:
                                if 40000 < all_shares < 60000 and curr > all_shares * 0.15 > price:
                                    return int(all_shares * 0.15 / price)
                                else:
                                    if 60000 < all_shares < 90000 and curr > all_shares * 0.08 > price:
                                        return int(all_shares * 0.08 / price)
                                    else:
                                        if 90000 < all_shares < 110000 and curr > all_shares * 0.06 > price:
                                            return int(all_shares * 0.06 / price)
                                        else:
                                            return qty_lots

    except Exception as er:
        print(er)

def rsi(candles: pandas.DataFrame) -> pandas.DataFrame:
    return ta.momentum.rsi(candles['close'],window = 20,fillna=True)