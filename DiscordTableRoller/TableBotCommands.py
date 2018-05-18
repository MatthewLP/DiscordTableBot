from discord.ext import commands

import TableBot

class TableBotCommands:
    """This class houses all the commands used in TableBot"""
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="Table", pass_context=True, aliases=["table"])
    async def table(self, ctx):
        '''Returns a list of all tables currently loaded. 
        "Table table_name" will list all the items in that table.
        "Table table_name item_name" gives you a full discription of the item
        "Table table_name item_name data_type" will give you just that data for that item
        
        There are four special data_types:
        name: If you ask for this you might be stupid so don't
        p_weight: Effects the probability of getting this item (1)
        brief: A short description given when you roll the item (1)
        description: A full discription excluding information from other data types
        
        (1): These are not given in the "Table table_name item_name" command.'''
        cmd = self.cmd_split(ctx)
        if len(cmd) == 1:
            say_lst = self.bot.table_list()
            say_lst.insert(0,"The following tables are loaded: \n\n")
            say = ''.join(say_lst)
        elif ctx.invoked_subcommand == None:
            say = ''.join(self.bot.table_query(cmd[1],\
                            cmd[2] if len(cmd) > 2 else None,\
                            cmd[3] if len(cmd) > 3 else None))
        else:
            return
        await self.bot.say(say)

    @table.command(name="Load", pass_context=True, aliases=["load"])
    async def load_files(self, ctx):
        '''Loads all tables stored in the the "./tables/" directory, use this only to update
        the tables when a new one is added.'''
        if self.bot.load_files():
            await self.bot.say("Files loaded")
        else:
            await self.bot.say("Failed to load")

    @table.command(name="Roll", pass_context=True, aliases=["roll"])
    async def roll_table(self, ctx):
        '''Picks a random item from the named table ("Table roll table_name") and gives you
        its name and a brief description of it.'''
        cmd = self.cmd_split(ctx)
        if len(cmd) < 3:
            out_str = ''.join(("I can't roll nothing. Try `",ctx.prefix,"table` to", \
                      " get a list of loaded tables."))
        else:
            out_str = ''.join(self.bot.roll_table(cmd[2]))
        await self.bot.say(out_str)

    def cmd_split(self, ctx: commands.Context):
        return ctx.message.content.split()

def setup(bot: TableBot):
    bot.add_cog(TableBotCommands(bot))