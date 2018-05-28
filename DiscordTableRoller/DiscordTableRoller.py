'''The main of the discord table roller defines bot gives it an on_ready and runs it'''
from TableBot import TableBot
import options

bot = TableBot(command_prefix=options.command_prefix, description=options.description)

@bot.event
async def on_ready():
    '''prints to console name and ID of the bot when it is done initializing'''
    if options.verbose is True:
        print("Bot Online!")
        print("Name: {}".format(bot.user.name))
        print("ID: {}".format(bot.user.id))


bot.run(options.token)
