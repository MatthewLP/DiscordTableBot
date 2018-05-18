import asyncio
import glob
import discord
import csv
from discord.ext import commands

from Table import Table

#from TableBotCommands import TableBotCommands as Cmds

class TableBot(commands.Bot):
    """description of class"""

    def __init__(self, command_prefix, formatter=None, description=None,
                 pm_help=False, **options):

        super().__init__(command_prefix, formatter,
                         description, pm_help, **options)

        self.load_extension('TableBotCommands')

        self.tables = {}
        self.load_files()
        #add initalizers for members as needed

    def load_files(self):
        self.tables.clear()
        for filename in glob.glob("tables/*.csv"):
            with open(filename, 'r') as csvfile:
                dialect = csv.Sniffer().sniff(csvfile.read(2048))
                csvfile.seek(0)
                Table(csv.reader(csvfile, dialect), self.tables)

        return True

    def table_query(self, name: str, item_name = None, data_type = None):
        '''Attempts to retrieve information on the table named param name,
        failure returns error messages to the user
        :param name: an alias for a table
            type: string
        :param item_name: the name of an item in the table (optional)
            type: string
        :param data_type: the name of a data type in the table (optional)
            type: string
        :return: a list of strings to be str.join()-ed before being sent to discord'''
        out_lst = []
        if name in self.tables:
            if item_name == None:
                out_lst.extend(('All items in ',name,':\n\n'))
                out_lst.extend(self.discord_item_list(self.tables[name].get_item_names()))
            else:
                out_lst.extend(self.tables[name].query(item_name,data_type))
        else:
            out_lst.extend(('There is no table called ',name,'.'))

        return out_lst

    def roll_table(self, name: str):
        '''Attempts to pick an item randomly from the table param name,
        failure returns an error message to the user
        :param name: an alias for a table
            type: string
        :return: a list of strings to be str.join()-ed before being sent to discord'''
        out_lst = []
        if name in self.tables:
            out_lst.extend(self.tables[name].roll())
        else:
            out_lst.extend(('There is no table called ',name,'.'))

        return out_lst

    def table_list(self):
        '''discord_item_lists all the keys in the table list'''
        out_lst = self.discord_item_list(self.tables.keys())

        return out_lst

    def discord_item_list(self, itemiterable):
        '''
        :param itemiterable: any iterable object with strings as entries
        :return: a list of the form:
                 ['`',key1,'` ','`',key2,'` ','`',key3,'` ', ect...]
                 ment to be used with str.join()'''
        out_lst = []
        for item in itemiterable:
            out_lst.extend(('`',item,'` '))

        return out_lst