'''The main of the discord table roller defines bot gives it an on_ready and runs it'''
from TableBot import TableBot

bot = TableBot(command_prefix='--', description='')

@bot.event
async def on_ready():
    '''prints to consle name and ID of the bot when it is done initializing'''
    print("Bot Online!")
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))


bot.run("NDQzMjI3NTUzODI2NjAzMDA5.DeoiOA.X_Lvi2yuHmZ4qFyEArx0erIB26k")
