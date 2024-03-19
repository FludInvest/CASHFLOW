from config import *
from mysql.connector import connect
import asyncio


async def get_connection():
    conection = connect(
        database=data_base['name'],
        host=data_base['host'],
        user=data_base['user'],
        password=data_base['password'],
        port=data_base['port'])

    cursor = conection.cursor(buffered=True)

    return conection, cursor


async def change_data(query, value = None) -> None:
    connection, cursor = await get_connection()
    if value is None:
        cursor.execute(query)
        connection.commit()
    else:
        cursor.execute(query,value)
        connection.commit()

    if connection.is_connected():
        connection.close()

async def fetchone(query,value = None):
    connection, cursor = await get_connection()
    if value is None:
        cursor.execute(query)
    else:
        cursor.execute(query,value)
    
    result = cursor.fetchone()

    if connection.is_connected():
        connection.close()
    
    return result[0]


async def fetchall(query,value = None):
    connection, cursor = await get_connection()
    if value is None:
        cursor.execute(query)
    else:
        cursor.execute(query,value)
    
    result = cursor.fetchall()

    if connection.is_connected():
        connection.close()
    
    return result


async def create_if_not_exists() -> None:
    try:
        connection, cursor = await get_connection()

        cursor.execute("""CREATE TABLE IF NOT EXISTS ACCOUNTS (
            ID INT ,
            ID_TINKOFF VARCHAR(255),
            BOT_WORK BOOL,
            QUANTITY_DEALS INTEGER,
            PROFIT FLOAT)""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS BUY (
            CODE VARCHAR(255),
            TICKER VARCHAR(255),
            PRICE FLOAT,
            QUANTITY_LOTS INTEGER)""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS SELL (
            CODE VARCHAR(255),
            TICKER VARCHAR(255),
            PRICE FLOAT,
            QUANTITY_LOTS INTEGER,
            SELL_PRICE FLOAT)""")


        cursor.execute("""CREATE TABLE IF NOT EXISTS EXCLUSION_LIST (
            LIST VARCHAR(255))""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS DEALS (
            TICKER VARCHAR(255),
            QUANTITY_LOTS INTEGER,
            AVG_PRICE FLOAT,
            STRATEGY VARCHAR(255))""")
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS START (
            TICKER VARCHAR(255),
            QUANTITY_LOTS INTEGER,
            AVG_PRICE FLOAT)""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS SIGNALS (
            TICKER VARCHAR(255))""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS ERRORS (
            TICKER VARCHAR(255),
            TEXT VARCHAR(255))""")

        connection.commit()

    except Exception as error_code:
        print("Error Base -> ", error_code)
        connection.close()
    finally:
        connection.close()

async def start_db() -> None:
    await change_data("DELETE FROM BUY")
    await change_data("DELETE FROM SELL")
    await change_data("DELETE FROM START")
    await change_data("DELETE FROM DEALS")
    await change_data("DELETE FROM ERRORS")


    if await fetchone("SELECT ID FROM ACCOUNTS") is None:
        await change_data("INSERT INTO ACCOUNTS (ID,ID_TINKOFF,BOT_WORK,QUANTITY_DEALS,PROFIT) VALUES (%s,%s,%s,%s,%s)",(0,tokens['tinkoff'],False,0,0,))

    else:
        if await fetchone("SELECT PROFIT FROM ACCOUNTS WHERE ID = 0") is None:
            await change_data("INSERT INTO ACCOUNTS (PROFIT) VALUES (%s)",(0,))

        if await fetchone("SELECT QUANTITY_DEALS FROM ACCOUNTS WHERE ID = 0") is None:
            await change_data("INSERT INTO ACCOUNTS (QUANTITY_DEALS) VALUES (%s)",(0,)) 

        if await fetchone("SELECT BOT_WORK FROM ACCOUNTS WHERE ID = 0") is not None:
            await change_data("UPDATE ACCOUNTS SET BOT_WORK = (%s)",(False,))

        if await fetchone("SELECT BOT_WORK FROM ACCOUNTS WHERE ID = 0") is None:
            await change_data("INSERT INTO ACCOUNTS (BOT_WORK) VALUES (%s)",(False,)) 

        if await fetchone("SELECT ID_TINKOFF FROM ACCOUNTS WHERE ID = 0") is None:
            await change_data("INSERT INTO ACCOUNTS (ID_TINKOFF) VALUES (%s)",(tokens['tinkoff'],))

if __name__ != "__main__":
    asyncio.run(create_if_not_exists())
    asyncio.run(start_db())


