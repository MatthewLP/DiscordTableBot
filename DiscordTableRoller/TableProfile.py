from discord.ext import commands
from TableBotCommands import cmd_split

NOT_OP = 'You do not have permission to access this profile.'

class TableProfile():
    """Contains a collection of table locations and preloaded tables that can be loaded
or unloaded from the bot with one command. Also has a list of OPed accounts that can
modify the profile. With an option that only OPs can load it (Default off)."""

    def __init__(self, bot, ctx):
        self.name = cmd_split(ctx)[-1]
        self.bot = bot
        self.OPs = {ctx.message.author.id:True} #True = curator, False = not
        self.loaders = {}
        self.tables = []
        self.table_names = []

    def push_op(self, ctx: commands.Context):
        if self.is_op(ctx):
            new_op = cmd_split(ctx)[-1]
            self.OPs[new_op[2:-2]] = False
            out_lst = [new_op, ' is now an OP for ', self.name]
        else:
            out_lst = [NOT_OP]
        return out_lst

    def pop_op(self, ctx: commands.Context):
        if self.is_op(ctx):
            un_opped = cmd_split(ctx)[-1][2:-2]
            if un_opped in self.OPs:
                if not self.OPs[un_opped]:
                    self.OPs.pop(un_opped)
                    out_lst = ['<@', un_opped, '> is no longer an OP.']
                else:
                    out_lst = ['You can not deOP the curator of this profile.']
            else:
                out_lst = ['<@', un_opped, '> is not an OP.']
        else:
            out_lst = [NOT_OP]
        return out_lst

    def is_op(self, ctx: commands.Context):
        return ctx.message.author.id in self.OPs
            
    def push_table()
