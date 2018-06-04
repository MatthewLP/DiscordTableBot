'''Defines the TableProfile class'''
import asyncio
from glob import glob
from os.path import normpath

from WithOPs_mixin import WithOPs_mixin
import TableBot
from Table import Table

class TableProfile(WithOPs_mixin):
    '''Contains a collection of table locations and preloaded tables that can be loaded
or unloaded from the bot with one command. Also has a list of OPed accounts that can
modify the profile. With an option that only OPs can load it (Default off).'''

    def __init__(self, bot, creater_id, name):
        super().__init__(creater_id, name)
        self.bot = bot
        self.tables = {}
        self.active = False
        self.op_activate_only = False

    @WithOPs_mixin.is_op
    async def push_table(self, caller_id, filepath):
        '''Adds the table found at 'filepath' to the list of tables if the file it exists.
:param caller_id: a uneque identifier for whatever originally called this method.
    type: anything hashable
:param filepath: the location of the table to be added to the profile.
    type: string
:return: a list of strings describing what has happened.'''
        if filepath.startswith(('http://', 'https://')):
            out_lst = ['Sorry I have yet to implement internet sources.']
        else:
            check = glob(filepath)
            if check:
                check = normpath(check[0])
                if check not in self.tables:
                    self.tables[check] = None
                    out_lst = ['`', filepath, '` has been added to ', self.name, '.']
                else:
                    out_lst = ['`', filepath, '` is already in ', self.name, '.']
                
                if self.active:
                    self.load(caller_id)
            else:
                out_lst = ['`', filepath, '` does not exist.']
        return out_lst

    @WithOPs_mixin.is_op
    def pop_table(self, caller_id, filepath):
        '''Removes the table at 'filepath' from the list of tables.
:param caller_id: a uneque identifier for whatever originally called this method.
    type: anything hashable
:param filepath: the location of the table to be removed from to the profile.
    type: string
:return: a list of strings describing what has happened.'''
        file = normpath(filepath)
        if file in self.tables:
            to_remove = self.tables.pop(file)
            if self.active:
                self.bot.remove(to_remove)
            out_lst = ['`', filepath, '` has been removed from ', self.name, '.']
        else:
            out_lst = ['`', filepath, '` is not in ', self.name, '.']
        return out_lst

    @WithOPs_mixin.is_curator
    def set_op_activate(self, caller_id, new_val: bool):
        '''Sets weather or not you have to be an OP to load and unload the profile.
:param caller_id: a uneque identifier for whatever originally called this method.
    type: anything hashable
:param new_val: True for requires OP status to activate'''
        self.op_activate_only = new_val

    def optional_is_op(func):
        '''Decorates the decorated function with WithOPs_mixin.is_op if the calling user
has to be an OP to load/unload.'''
        def wraper(self, *args, **kwargs):
            @WithOPs_mixin.is_op
            def with_op(self, *args, **kwargs):
                return func(self, *args, **kwargs)

            def sans_op(self, *args, **kwargs):
                return func(self, *args, **kwargs)

            return with_op(self, *args, **kwargs) \
                if self.op_activate_only \
                else sans_op(self, *args, **kwargs)
        return wraper

    @optional_is_op
    def load(self, caller_id):
        '''Loads all tables in the profile into the bot.
:param caller_id: a uneque identifier for whatever originally called this method.
    type: anything hashable
:return: a list of strings describing what has happened.'''
        updater = {}
        for key in self.tables:
            if self.tables[key]:
                updater.update([(i, self.tables[key]) for i in self.tables[key].aliases])
                continue
            self.tables[key] = Table(key, updater)

        self.bot.update(updater)
        self.active = True
        return [self.name, ' has been loaded.']

    @optional_is_op
    def unload(self, caller_id):
        '''Unloads all tables in the profile from the bot.
:param caller_id: a uneque identifier for whatever originally called this method.
    type: anything hashable
:return: a list of strings describing what has happened.'''

        if self.active:
            for key in self.tables:
                self.bot.remove(self.tables[key])
                self.tables[key] = None
            out_lst = [self.name, ' has been unloaded.']
            self.active = False
        else:
            out_lst = [self.name, ' is not loaded.']
        return out_lst

    @optional_is_op
    def reload(self, caller_id):
        '''Shortcut for:
TableProfile.unload
TableProfile.load'''
        out_lst = self.unload(caller_id).append('\n')
        out_lst.extend(self.load(caller_id))
        return out_lst
