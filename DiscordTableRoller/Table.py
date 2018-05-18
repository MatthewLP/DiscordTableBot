import csv
import asyncio
import random

class Table:
    """
    This class handles all the information and math associated 
    with the indevidual tables loaded into the bot
    """

    def __init__(self, contents: csv.DictReader, container = {}):
        '''
        :param contents: the contents of a csv
                type: csv.DictReader
        :param container: the dict containing all Table names
                type: dict'''
        self.data = {}
        self.weighted = False
        self.briefs = False
        self.descriptions = False
        self.out_of = 0

        contents = list(contents)

        for alias in contents[0]:
            container[alias] = self

        for i in range(len(contents[1])):
            if contents[1][i] == 'name':
                name_index = i
            elif contents[1][i] == 'p_weight':
                self.weighted = True
            elif contents[1][i] == 'brief':
                self.briefs = True
            elif contents[1][i] == 'description':
                self.description = True

        for row in contents[2:]:
            row_dict = {}

            self.data[row[name_index]] = row_dict

            for i in range(len(row)):
                if i != name_index:
                    if contents[1][i] == '':
                        break
                    row_dict[contents[1][i]] = row[i]

            self.out_of += int(row_dict.get('p_weight',1))

        self.data_order = self.data.items()

    def roll(self):
        '''sellects one of the items at random (weighted if the 
        table has a 'p_weight' colomn)
        return: a list of strings to be str.join()-ed containing the chosen 
                item's name and its brief if the table had that colomn'''
        loc = random.randint(0,self.out_of - 1)
        total = 0
        itr = iter(self.data_order)
        while True:
            at = next(itr)
            total += int(at[1].get('p_weight',1))
            if loc < total:
                break

        out_lst = [at[0]]
        if self.briefs:
            out_lst.extend((": ",at[1]['brief']))

        return out_lst

    def query(self, name: str, data_type = None):
        '''attempts to retrieve data on param name, all but the 
        brief & p_wieght if param data_type is None or attempts to 
        retrieve the data with the key param data_type if either 
        case fails it returns an error message

        :param name: the name of the object you are attempting to retrive
            type: string
        :param data_type: the name of the data you are attempting to 
                          retrive. None returns all but brief & p_weight
            type: string
        :return: a list of strings to be str.join()-ed before sent to discord
        '''
        out_lst = []

        if name in self.data:
            if data_type == None:
                out_lst.extend(('```\n',name,':\n'))
                item_data = self.data[name].items()
                for pair in item_data:
                    if pair[0] != 'p_weight'   \
                        and pair[0] != 'brief' \
                        and pair[0] != 'description':

                        out_lst.extend((pair[0],': ',pair[1],'\n'))
                if self.descriptions:
                    out_lst.extend(('\n',self.data[name]['description']))
                elif self.briefs:
                    out_lst.extend(('\n',self.data[name]['brief']))
                out_lst.append('```')

            elif data_type in self.data[name]:
                out_lst.extend(('```\n',name,':\n',data_type,': ', \
                         self.data[name][data_type],'```'))
            else:
                out_lst.extend(('`',name,'` does not have any `', \
                    data_type,'`.'))
        else:
            out_lst.extend(('`',name,'` is not an item in this table.'))

        return out_lst

    def get_item_names(self):
        return self.data.keys()

