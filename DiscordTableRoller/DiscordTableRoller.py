from TableBot import TableBot

bot = TableBot(command_prefix='?', description='')

@bot.event
async def on_ready():
    print("Bot Online!")
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))

bot.run("NDQzMjI3NTUzODI2NjAzMDA5.DdKTgA.brvgSaAfPlpzZKDyF3UBzTWTUwM")