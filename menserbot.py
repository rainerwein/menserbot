import discord
from discord.commands.context import ApplicationContext
from discord.ext import commands
from discord.commands import Option

from datetime import datetime
import asyncio
import signal

from menser import get_plan, Plan
from helper import *
from config import TOKEN_MENSERBOT, GET_DELAY, DEBUG_GUILDS

bot = commands.Bot('', activity=discord.Activity(name='Speiseplan', type=discord.ActivityType.watching))
messages = []

@bot.slash_command(description='Sich automatisch aktualisierender Mensaplan')
async def mensa(ctx, mensa: Option(str, description="Mensa auswählen", choices=[mensa.value for mensa in Mensa], default=Mensa.EICH), veggie: Option(bool, "Nur vegetarische/vegane Gerichte", default=True)):
    mensaEnum = Mensa(mensa)
    embed = discord.Embed(title=f'Speiseplan {mensaEnum.value}', description="*Lädt...*", color=0x49db39 if veggie else 0x03a1fc)

    interaction = await ctx.respond(embed=embed)
    interaction_message = await interaction.original_message()
    real_message = await interaction_message.channel.fetch_message(interaction_message.id)

    bot.loop.create_task(job(message=real_message, embed=embed, mensa=mensaEnum, veggie=veggie))
    insert_values_into_table(guild_id=real_message.guild.id, mensa=mensaEnum, channel_id=real_message.channel.id, message_id=real_message.id, veggie=veggie)
    messages.append(real_message)

@bot.slash_command(description='Nachricht löschen', guild_ids=DEBUG_GUILDS)
async def löschen(ctx: ApplicationContext, message_id: Option(str, description='Zu löschende Nachricht (ID)')):
    try:
        message = await ctx.channel.fetch_message(int(message_id))
        if message in messages:
            await message.delete()
            delete_from_db(guild_id=message.guild.id, channel_id=message.channel.id, message_id=message.id)
            messages.remove(message)
            await ctx.respond('Nachricht gelöscht.\n*Diese Nachricht verschwindet in 10 Sekunden...*')
            await asyncio.sleep(10)
            await ctx.delete()
            return
        else:
            await ctx.respond('Keine Nachricht von mir!\n*Diese Nachricht verschwindet in 10 Sekunden...*')
            await asyncio.sleep(10)
            await ctx.delete()
        return
    except discord.NotFound:
        await ctx.respond('Nachricht nicht gefunden! Richtiger Channel?\n*Diese Nachricht verschwindet in 10 Sekunden...*')
        await asyncio.sleep(10)
        await ctx.delete()
        return
    except Exception as e:
        print(e)


   
    

# @tasks.loop(seconds=5)
async def job(message, embed: discord.Embed, mensa: Mensa, veggie: bool):
    while True:
        embed.clear_fields()
        embed.remove_author()
        embed.description = ''
        embed.title = f'Speiseplan {mensa.value}'
        embed.color = 0x49db39 if veggie else 0x03a1fc
        if veggie: 
            embed.set_author(name='Veggie\u200b', url='https://xkcd.com/1587/', icon_url='https://cdn-icons-png.flaticon.com/512/723/723633.png')
        embed.set_footer(text=f'Stand:  {datetime.now().strftime("%d.%m.%Y - %H:%M:%S")}')

        plan: Plan = await get_plan(mensa=mensa, veggie=veggie)
        for day in plan.days:
            embed.add_field(name=day.day, value="".join(day.meals), inline=False)

        try:
            await message.edit(embed=embed)
        except discord.NotFound:
            delete_from_db(guild_id=message.guild.id, channel_id=message.channel.id, message_id=message.id)
            break

        await asyncio.sleep(GET_DELAY)

async def refresh_message(message) -> discord.Message: 
    guild = bot.get_guild(message.guild.id)
    channel = guild.get_channel(message.channel.id)
    return await channel.fetch_message(message.id)

@bot.event
async def on_ready():
    dbList = get_info_from_db()
    for db in dbList:
        try:
            guild = bot.get_guild(db.guild_id)
            channel = guild.get_channel(db.channel_id)
            msg = await channel.fetch_message(db.message_id)
            messages.append(msg)
            bot.loop.create_task(job(message=msg, embed=msg.embeds[0], mensa=db.mensa, veggie=db.veggie))

        except discord.NotFound:
            #print('message not found on startup, deleting...')
            delete_from_db(guild_id=db.guild_id, channel_id=db.channel_id, message_id=db.message_id)
            pass
    print(f'{bot.user} has connected.')

async def on_shutdown():
    if not messages:
        return
    for message in messages:
        try:
            message = await refresh_message(message)
            embed: discord.Embed = message.embeds[0]

            embed.title = f'{embed.title} *[BOT GESTOPPT]*'
            embed.color = 0xFF0000
            embed.set_footer(text=f'{embed.footer.text} [BOT GESTOPPT]')
            await message.edit(embed=message.embeds[0], view=None)
        except discord.NotFound:
            delete_from_db(guild_id=message.guild.id, channel_id=message.channel.id, message_id=message.id)
            pass

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

if __name__ == '__main__':
    check_if_table_exists()

    #der ganze scheiß ist nur hier weil ich die Nachricht löschen will, wenn der Bot beendet wird
    loop = bot.loop

    try:
        loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
        loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
    except NotImplementedError:
        pass

    async def runner():
        try:
            await bot.start(TOKEN_MENSERBOT)
        finally:
            if not bot.is_closed():
                await bot.close()

    def stop_loop_on_completion(f):
        loop.stop()

    future = asyncio.ensure_future(runner(), loop=loop)
    future.add_done_callback(stop_loop_on_completion)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
        #print('Received signal to terminate bot and event loop.')
    finally:
        loop.run_until_complete(on_shutdown())

        future.remove_done_callback(stop_loop_on_completion)
        #print('Cleaning up tasks.')
        cleanup_loop(loop)
           