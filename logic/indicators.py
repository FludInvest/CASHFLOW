import pandas
import ta.trend

def convert_money_for_qty(units, nano):
    return units + nano / 1e9


def reconvert_money(num):
    return int(num), int((num - int(num)) * 1e9)


def convert_money(num):
    return num.units + num.nano / 1e9


def get_heiken_ashi(candles) -> pandas.DataFrame:
    df_HA = candles.copy()
    df_HA['close']=(df_HA['open']+ df_HA['high']+ df_HA['low']+df_HA['close'])/4
 
    for i in range(0, len(candles)):
        if i == 0:
            df_HA['open'][i]= ( (df_HA['open'][i] + df_HA['close'][i] )/ 2)
        else:
            df_HA['open'][i] = ( (df_HA['open'][i-1] + df_HA['close'][i-1] )/ 2)
 
    df_HA['high']=df_HA[['open','close','high']].max(axis=1)
    df_HA['low']=df_HA[['open','close','low']].min(axis=1)

    return df_HA


def get_trande(candles,num):
    pass

