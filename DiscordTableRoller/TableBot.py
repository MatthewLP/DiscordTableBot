'''Defines the Table Bot class, a child of discord.py's Bot class and the function
discord_item_list'''
import glob
import traceback
from discord.ext import commands

from Table import Table
from TableProfile import TableProfile

#from TableBotCommands import TableBotCommands as Cmds

class TableBot(commands.Bot):
    '''A discord.py bot with added functionallity for randomly sellecting entries of a
tables it has loaded and displaying information on those tables to users.'''

    def __init__(self, command_prefix, formatter=None, description=None,
                 pm_help=False, **options):

        super().__init__(command_prefix, formatter,
                         description, pm_help, **options)

        self.load_extension('TableBotCommands')

        self.tables = {}
        self.profiles = {}
        self.load_files()
        #add initalizers for members as needed

    def load_files(self):
        '''Attempts to load every csv file in the ./tables/ directory into table objects'''
        try:
            self.tables.clear()
            for filename in glob.glob("tables/*.csv"):
                Table(filename, self.tables)
        except():
            traceback.print_exc()
            return False

        return True

    def update(self, extention):
        '''Adds all (alias, table) pairs in :extention: to the loaded tables.
:param extention: a collection of (alias, table) pairs
    Type: a dict: {alias: table,...} or other itterable: [(alias, table),...]'''
        self.tables.update(extention)

    def remove(self, table: Table):
        '''Removes all instances of the object :table: from the list of loaded tables
:param table: a table to be removed
    type: Table'''
        for alias in table.aliases:
            if self.tables.get(alias, False) is table:
                self.tables.pop(alias)

    def table_query(self, name: str, item_name=None, *rcrsv_call_data):
        '''Attempts to retrieve information on the table :name:,
        failure returns error messages to the user
        :param name: an alias for a table
            type: string
        :param item_name: the name of an item in the table (optional)
            type: string
        :param *rcrsv_call_data: the names of recursive tables' entries, potentially ending
                      with a data type in the last table (optional)
            type: string
        :return: a list of strings describing what happened.'''
        out_lst = []
        if name in self.tables:
            if not item_name:
                out_lst.extend(('All items in ', name, ':\n\n'))
                out_lst.extend(discord_item_list(self.tables[name].get_item_names()))
            else:
                out_lst.extend(self.tables[name].query(item_name, *rcrsv_call_data))
        else:
            out_lst.extend(('There is no table called `', name, '`.'))

        return out_lst

    def roll_table(self, name: str):
        '''Attempts to pick an item randomly from the table param name,
        failure returns an error message to the user
        :param name: an alias for a table
            type: string
        :return: a list of strings describing what happened.'''
        out_lst = []
        if name in self.tables:
            out_lst.extend(self.tables[name].roll())
        else:
            out_lst.extend(('There is no table called `', name, '`.'))

        return out_lst

    def table_list(self):
        '''discord_item_lists all the keys in the table list'''
        out_lst = discord_item_list(self.tables.keys())

        return out_lst

    def add_profile(self, name: str, user_id):
        '''Adds a new profile to the bot named :name: with the curator set to :user_id:
:param name: the name the profile is to be given.
    type: string
:param user_id: A uneque identifier for the user who called this function.
    type: any hashable
:return: a list of strings describing what happened.'''
        if name in self.profiles:
            out_lst = [name, ' already exists, please try a different name.']
        else:
            self.profiles[name] = TableProfile(self, user_id, name)
            out_lst = [name, ' has been created.']
        return out_lst

    def get_profile(self, name: str):
        '''Retrieves the TableProfile with name :name: throws an error if :name: is not
a profile.
:param name: the name of the profile to be retrieved
    type: string
:return: a TableProfile'''
        return self.profiles[name]

    def del_profile(self, name: str, user_id):
        '''Deletes the TableProfile with name :name: if the :user_id: is the curator of the
profile.'''
        if name in self.profiles:
            if self.profiles[name].bool_is_curator(user_id):
                self.profiles.pop(name)
                return [name, ' has been deleted.']
            return ['You do not have permission to delete ', name, '.']
        return [name, ' is not a profile here.']

    def profile_list(self):
        return discord_item_list(self.profiles.keys())

def discord_item_list(itemiterable):
    '''
    :param itemiterable: any iterable object with strings as entries
    :return: a list of the form:
                ['`',item1,'` ','`',item2,'` ','`',item3,'` ', ect...]'''
    out_lst = []
    for item in itemiterable:
        out_lst.extend(('`', item, '` '))

    return out_lst