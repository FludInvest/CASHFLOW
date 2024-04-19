from mysql.connector import connect
from dotenv import load_dotenv
from log_folder._log import add_log
import os
import asyncio


class MySQLConnection:
    async def get_connection(self):
        try:
            load_dotenv(".env")

            connection = connect(
                database=os.getenv("BASE_NAME"),
                host=os.getenv("HOST"),
                user=os.getenv("USER"),
                password=os.getenv("PASSWORD"),
                port=os.getenv("PORT"))
            
            cursor = connection.cursor(buffered=True)

            return connection, cursor

        except Exception as error_code:
            add_log(error_code)

            if connection.is_connected():
                connection.close()

    async def on_start(self) -> None:
        try:
            connection , cursor = await self.get_connection()

            cursor.execute("""CREATE TABLE IF NOT EXISTS ACCOUNT_INFO (
                BOT_WORK BOOL,
                QUANTITY_DEALS INTEGER,
                PROFIT FLOAT)""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS BUY (
                TICKER VARCHAR(255),
                PRICE FLOAT,
                QUANTITY_LOTS INTEGER)""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS SELL (
                TICKER VARCHAR(255),
                PRICE FLOAT,
                QUANTITY_LOTS INTEGER,
                SELL_PRICE FLOAT)""")


            cursor.execute("""CREATE TABLE IF NOT EXISTS EXCLUSION_LIST (
                LIST VARCHAR(255))""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS DEALS (
                TICKER VARCHAR(255),
                QUANTITY_LOTS INTEGER,
                AVG_PRICE FLOAT)""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS START (
                TICKER VARCHAR(255),
                AVG_PRICE FLOAT,
                QUANTITY_LOTS INTEGER)""")

            connection.commit()

            if await Get().fetchone("SELECT BOT_WORK FROM ACCOUNT_INFO") is None:
                await Get().change_data("DELETE FROM ACCOUNT_INFO")
                await Get().change_data("INSERT INTO ACCOUNT_INFO VALUES (%s,%s,%s)",(False,0,0,))

            await Get().change_data("DELETE FROM SELL")
            await Get().change_data("DELETE FROM BUY")
            await Get().change_data("DELETE FROM START")
            await Get().change_data("DELETE FROM DEALS")
            
        except Exception as error_code:
            add_log(error_code)

        
class Get(MySQLConnection):
    async def change_data(self,query,values = None) -> None:
        connection , cursor = await self.get_connection()
        cursor.execute(query, values)
        connection.commit()

        if connection.is_connected():
            connection.close()

    async def fetchone(self,query,values = None):
        connection , cursor = await self.get_connection()

        if values is not None:
            cursor.execute(query, values)
        else:
            cursor.execute(query)

        if connection.is_connected():
            connection.close()

        return cursor.fetchone()
    
    async def fetchall(self,query,values = None):
        connection , cursor = await self.get_connection()
        if values is not None:
            cursor.execute(query, values)
        else:
            cursor.execute(query)

        if connection.is_connected():
            connection.close()

        return cursor.fetchall()

