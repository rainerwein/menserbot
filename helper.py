import asyncio
import sqlite3
from enum import Enum
import traceback

class Mensa(Enum):
    SUED = 'Südmensa'
    LMP = 'Langemarckplatz'
    TRIE = 'Mensataria Triesdorf'
    EICH = 'Mensa Eichstätt'
    CAFE_KOCH = 'Cafeteria Kochstraße'

def api_url(mensa: Mensa) -> str:
    switch = {
        Mensa.SUED: 'https://www.max-manager.de/daten-extern/sw-erlangen-nuernberg/xml/mensa-sued.xml',
        Mensa.LMP: 'https://www.max-manager.de/daten-extern/sw-erlangen-nuernberg/xml/mensa-lmp.xml',
        Mensa.TRIE: 'https://www.max-manager.de/daten-extern/sw-erlangen-nuernberg/xml/mensateria-triesdorf.xml',
        Mensa.CAFE_KOCH: 'https://www.max-manager.de/daten-extern/sw-erlangen-nuernberg/xml/cafeteria-kochstr.xml',
        Mensa.EICH: 'https://www.max-manager.de/daten-extern/sw-erlangen-nuernberg/xml/mensa-eichstaett.xml',
    }
    return switch.get(mensa)

#joinked from discord.client
def _cancel_tasks(loop: asyncio.AbstractEventLoop) -> None:
    tasks = {t for t in asyncio.all_tasks(loop=loop) if not t.done()}

    if not tasks:
        return

    #print(f'Cleaning up after {len(tasks)} tasks')
    for task in tasks:
        task.cancel()

    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    #print('All tasks finished cancelling.')

    for task in tasks:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler({
                'message': 'Unhandled exception during Client.run shutdown.',
                'exception': task.exception(),
                'task': task
            })

def cleanup_loop(loop: asyncio.AbstractEventLoop) -> None:
    try:
        _cancel_tasks(loop)
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        #print('Closing the event loop.')
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
    def __init__(self, guild_id: int, mensa: Mensa, channel_id: int, message_id: int, veggie: bool):
        self.guild_id = guild_id
        self.mensa = mensa
        self.channel_id = channel_id
        self.message_id = message_id
        self.veggie = veggie

def create_table(dbname=dbname, table_name=table_name, headers=db_headers):
    try:
        query = f'CREATE TABLE IF NOT EXISTS {table_name} {tuple(headers)}'
        cursor.execute(query)
        return
    except sqlite3.OperationalError as e:
        print(e)
        return

def insert_values_into_table(guild_id, mensa: Mensa, channel_id, message_id, veggie, dbname=dbname, table_name=table_name):
    try:
        query = f'INSERT INTO {table_name} VALUES{tuple([guild_id, mensa.name, channel_id, message_id, veggie])}'
        cursor.execute(query)
        connection.commit()
        return
    except sqlite3.OperationalError as e:
        print(e)
        return

def delete_from_db(guild_id, channel_id, message_id, dbname=dbname, table_name=table_name):
    try:
        query = f'DELETE FROM {table_name} WHERE guild_id = {guild_id} AND channel_id = {channel_id} AND message_id = {message_id}'
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
            try:
                lis.append(MenserMessage(guild_id=row[0], mensa=Mensa[row[1]], channel_id=row[2], message_id=row[3], veggie=bool(row[4])))
            except Exception:
                traceback.print_exc()
        return lis
    except sqlite3.OperationalError as e:
        print(e)
        return []
        