import asyncio
import signal
import sqlite3
from enum import Enum

class Mensa(Enum):
    SUED = 'sued'
    LMP = 'lmp'

def full_mensa_name(mensa: Mensa) -> str:
    if mensa == Mensa.SUED:
        return "Südmensa"
    elif mensa == Mensa.LMP:
        return "Langemarckplatz"

def enum_from_full_mensa_name(full_mensa_name: str) -> Mensa:
    if full_mensa_name == "Südmensa":
        return Mensa.SUED
    elif full_mensa_name == "Langemarckplatz":
        return Mensa.LMP

#joinked from discord.client
def _cancel_tasks(loop: asyncio.AbstractEventLoop) -> None:
    tasks = {t for t in asyncio.all_tasks(loop=loop) if not t.done()}

    if not tasks:
        return

    print(f'Cleaning up after {len(tasks)} tasks')
    for task in tasks:
        task.cancel()

    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    print('All tasks finished cancelling.')

    for task in tasks:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler({
                'message': 'Unhandled exception during Client.run shutdown.',
                'exception': task.exception(),
                'task': task
            })

def _cleanup_loop(loop: asyncio.AbstractEventLoop) -> None:
    try:
        _cancel_tasks(loop)
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        print('Closing the event loop.')
        loop.close()

#
# Datenbank Gedöns
#

dbname = 'mensa.db'
table_name = 'mensa'
db_headers = ['guild_id', 'mensa', 'channel_id', 'message_id', 'veggie']
connection = sqlite3.connect(dbname)
cursor = connection.cursor()

class MenserMessage:
    def __init__(self, guild_id, mensa: Mensa, channel_id, message_id, veggie):
        self.guild_id = guild_id
        self.mensa = mensa
        self.channel_id = channel_id
        self.message_id = message_id
        self.veggie = veggie

def create_table(dbname=dbname, table_name=table_name, headers=db_headers):
    try:
        query = f'CREATE TABLE IF NOT EXISTS {table_name} {tuple(headers)}'
        print(query)
        cursor.execute(query)
        return
    except sqlite3.OperationalError as e:
        print(e)
        return

def insert_values_into_table(guild_id, mensa: Mensa, channel_id, message_id, veggie, dbname=dbname, table_name=table_name):
    try:
        query = f'INSERT INTO {table_name} VALUES{tuple([guild_id, mensa.value, channel_id, message_id, veggie])}'
        print(query)
        cursor.execute(query)
        connection.commit()
        return
    except sqlite3.OperationalError as e:
        print(e)
        return

def delete_from_db(guild_id, channel_id, message_id, dbname=dbname, table_name=table_name):
    try:
        query = f'DELETE FROM {table_name} WHERE guild_id = {guild_id} AND channel_id = {channel_id} AND message_id = {message_id}'
        print(query)
        cursor.execute(query)
        connection.commit()
        return
    except sqlite3.OperationalError as e:
        print(e)
        return

def check_if_table_exists(dbname=dbname, table_name=table_name, tableheaders=db_headers):
    try:
        query = 'SELECT * From ' + table_name
        cursor.execute(query)
    except sqlite3.OperationalError as e:
        create_table(dbname, table_name, tableheaders)

def get_info_from_db(dbname=dbname, table_name=table_name) -> list:
    try:
        query = 'SELECT * FROM ' + table_name
        cursor.execute(query)
        result = cursor.fetchall()
        lis = []
        for row in result:
            lis.append(MenserMessage(row[0], Mensa(row[1]), row[2], row[3], row[4]))
        return lis
    except sqlite3.OperationalError as e:
        print(e)
        return []