'''Defines all the discord.py commands used by table bot inside the TableBotCommands class
and a setup function used by the TableBot class when initializing'''
import shlex
import functools
from discord.ext import commands

import TableBot

BOOL_DICT = {'T':True, 't':True, 'true':True, 'True':True,
             'F':False, 'f':False, 'false':False, 'False':False}

def if_no_subcommand(func):
    @functools.wraps(func)
    async def wraper0(self, ctx):
        if ctx.invoked_subcommand is None:
            return await func(self, ctx)
        return
    return wraper0

class TableBotCommands:
    """This class houses all the commands used in TableBot"""
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name = "Table", pass_context = True, aliases = ["table"])
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
        cmd = cmd_split(ctx)
        if len(cmd) == 1:
            say_lst = self.bot.table_list()
            say_lst.insert(0, "The following tables are loaded: \n\n")
            say = ''.join(say_lst)
        elif ctx.invoked_subcommand is None:
            say = ''.join(self.bot.table_query(*cmd[1:]))
        else:
            return
        await self.bot.say(say)

    @table.command(name="Load", aliases=["load"])
    async def load_files(self):
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
        cmd = cmd_split(ctx)
        if len(cmd) < 3:
            out_str = ''.join(("I can't roll nothing. Try `", ctx.prefix, "table` to", \
                      " get a list of loaded tables."))
        else:
            out_lst = []
            for table in cmd[2:]:
                out_lst.append('\n')
                out_lst.extend(self.bot.roll_table(table))
            out_str = ''.join(out_lst[1:])
        await self.bot.say(out_str)

    @commands.group(name = "profile", pass_context = True, aliases = ["Profile"])
    async def profile(self, ctx):
        '''Returns a list of all loaded profiles.'''
        if ctx.invoked_subcommand is None:
            say_lst = self.bot.profile_list()
            say_lst.insert(0, "The following profiles are loaded: \n\n")
            say = ''.join(say_lst)
        else:
            return
        await self.bot.say(say)

    @profile.command(name = "Create", pass_context = True, aliases = ["create"])
    async def create_profile(self, ctx):
        '''Creates a table profile, and sets you as the curator.'''
        user_id, cmd = id_and_cmd(ctx)
        if len(cmd) == 2:
            out_lst = ['Try again with a profile name.']
        else:
            out_lst = self.bot.add_profile(cmd[2], user_id)
        await self.bot.say(''.join(out_lst))

    @profile.command(name = "Add", pass_context = True, aliases = ["add"])
    async def add_table_to_profile(self, ctx):
        '''Adds a table to a profile.
must be in the form [add|Add] [profile name] [table file path ~~or url~~]
requires OP privilage with the profile'''
        user_id, cmd = id_and_cmd(ctx)
        if len(cmd) == 2:
            out_lst = ['I require a profile name and file path.']
        elif len(cmd) == 3:
            out_lst = ['I require a file path.']
        else:
            name, path = cmd[2:4]
            try:
                profile = self.bot.get_profile(name)
                out_lst = await profile.push_table(user_id, path)
            except KeyError as error:
                out_lst = ['There is no profile named ', name]
        await self.bot.say(''.join(out_lst))

    def _only_need_profile_name(num_commands=2):
        '''Converts a function of the form (self, ctx) -> list of strings into
a coroutine of the form (self, ctx) that outputs to self.bot.say'''
        def actual_decorator(func):
            @functools.wraps(func)
            async def wraper1(self, ctx):
                cmd = cmd_split(ctx)
                if len(cmd) <= num_commands:
                    out_lst = ['I can\'t work with nothing, add a profile name.']
                else:
                    try:
                        out_lst = func(self, ctx)
                    except KeyError as error:
                        out_lst = ['There is no profile named ', cmd[num_commands]]
                await self.bot.say(''.join(out_lst))
            return wraper1
        return actual_decorator

    @profile.command("Remove", pass_context = True, aliases = ["remove", "rem", "Rem"])
    @_only_need_profile_name()
    def remove_table_from_profile(self, ctx):
        '''Removes a table from a profile.
must be in the form [remove|Remove|rem|Rem] [profile name]
requires OP privilage with the profile'''
        user_id, cmd = id_and_cmd(ctx)
        name = cmd[2]
        return self.bot.del_profile(name, user_id)

    @profile.command("load", pass_context = True, aliases = ["Load"])
    @_only_need_profile_name()
    def load_profile(self, ctx):
        '''Loads the profile's tables into the active table list.
must be in the form [load|Load] [profile name]
May require OP privilage with the profile'''
        user_id, cmd = id_and_cmd(ctx)
        name = cmd[2]
        profile = self.bot.get_profile(name)
        return profile.load(user_id)

    @profile.command("unload", pass_context = True, aliases = ["Unload"])
    @_only_need_profile_name()
    def unload_profile(self, ctx):
        '''Unloads the profile's tables from the active table list.
must be in the form [unload|Unload] [profile name]
May require OP privilage with the profile'''
        user_id, cmd = id_and_cmd(ctx)
        name = cmd[2]
        profile = self.bot.get_profile(name)
        return profile.unload(user_id)

    def _do_on_all_mentions(num_commands=2):
        '''Converts a (self, profile, op_id, user_id) -> list of strings signature into a
(self, ctx) -> list of strings signature'''
        def actual_decorator(func):
            def wraper2(self, ctx):
                user_id, cmd = id_and_cmd(ctx)
                name = cmd[num_commands]
                profile = self.bot.get_profile(name)
                out_lst = []
                for mention in ctx.message.raw_mentions:
                    out_lst.extend(func(self, profile, user_id, mention))
                    out_lst.append('\n')
                if not out_lst:
                    out_lst.append('You need to mention at least one user.')
                return out_lst
            try:
                wraper2.__doc__ = func.__doc__
            except:
                pass
            return wraper2
        return actual_decorator

    @profile.group("OP", pass_context = True)
    @if_no_subcommand
    @_only_need_profile_name()
    @_do_on_all_mentions()
    def profile_op(self, profile, op_id, user_id):
        '''Gives all mentioned users OP privilages'''
        return profile.push_op(op_id, user_id)

    @profile_op.command("revoke", pass_context = True, aliases = ["Revoke"])
    @_only_need_profile_name(3)
    @_do_on_all_mentions(3)
    def profile_op_revoke(self, profile, op_id, user_id):
        return profile.pop_op(op_id, user_id)

    @profile_op.command("require_for_load", pass_context = True, aliases = ["rfl"])
    @_only_need_profile_name(3)
    def profile_op_load(self, ctx):
        user_id, cmd = id_and_cmd(ctx)
        name = cmd[3]
        profile = self.bot.get_profile(name)
        if len(cmd) < 5:
            out_lst = profile.flip_op_activate(user_id)
        else:
            try:
                out_lst = profile.set_op_activate(user_id, BOOL_DICT[cmd[4]])
            except KeyError as error:
                out_lst = profile.flip_op_activate(user_id)
        if out_lst is None:
            out_lst = [profile.name, ' will ', '' if profile.get_op_activate() else 'not ',
                       'require OP privilage to load and unload.']
        return out_lst

def id_and_cmd(ctx: commands.Context):
    '''Returns the message author id and the output of cmd_split'''
    return ctx.message.author.id, cmd_split(ctx)

def cmd_split(ctx: commands.Context):
    '''Splits a discord context message into pieces at white spaces not between quotes'''
    return shlex.split(ctx.message.content)

def setup(bot: TableBot):
    '''this string exists to make pylint shut up'''
    bot.add_cog(TableBotCommands(bot))
