import csv
import asyncio
import random
import io

class Table:
    """
    This class handles all the information and math associated 
    with the indevidual tables loaded into the bot
    """

    def __init__(self, filepath, container = {}, parents = []):
        '''
        :param filepath: the path to the file to attempt to load
                type: string
        :param container: (optional) a dictionary to which all Table aliases
                          will be added as keys to this table
                type: dict
        :param parents: (optional) a list of all parent table paths, used
                        to ensure infinite recursion does not occur
                type: list'''
        self.data = {}
        self.columns = {}
        self.aliases = []
        self.filepath = filepath
        self.out_of = 0
        
        with io.open(filepath, 'r', encoding='utf8') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read())
            csvfile.seek(0)
            contents = list(csv.reader(csvfile, dialect))

        for alias in contents[0]:
            container[alias] = self
            self.aliases.append(alias)
        
            j = 0
            used_columns = []
        for i in range(len(contents[1])):
            if contents[1][i] == 'name':
                name_index = i
            elif contents[1][i] != '':
                self.columns[contents[1][i]] = j
                used_columns.append(i)
                j += 1

        for row in contents[2:]:
            row_lst = []

            for i in used_columns:
                row_lst.append(row[i])

            self.out_of += self._p_weight(row_lst)
            self.data[row[name_index]] = tuple(row_lst)

    def roll(self):
        '''sellects one of the items at random (weighted if the 
        table has a 'p_weight' colomn)
        return: a list of strings to be str.join()-ed containing the chosen 
                item's name and its brief if the table had that colomn'''
        loc = random.randint(0,self.out_of - 1)
        total = 0
        itr = iter(self.data)
        while True:
            at = next(itr)
            total += self._p_weight(self.data[at])
            if loc < total:
                break

        out_lst = [at]
        if 'brief' in self.columns:
            out_lst.extend((": ",self._get_data(at,'brief')))

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
                for c_key in self.columns:
                    if c_key != 'p_weight'   \
                        and c_key != 'brief' \
                        and c_key != 'description':
                        out_lst.extend((c_key,': ',self._get_data(name, c_key),'\n'))

                if 'description' in self.columns:
                    out_lst.extend(('\n',self._get_data(name,'description')))
                elif 'brief' in self.columns:
                    out_lst.extend(('\n',self._get_data(name,'brief')))
                out_lst.append('```')

            elif data_type in self.columns:
                out_lst.extend(('```\n',name,':\n',data_type,': ', \
                         self._get_data(name,data_type),'```'))
            else:
                out_lst.extend(('`',name,'` does not have any `', \
                    data_type,'`.'))
        else:
            out_lst.extend(('`',name,'` is not an item in this table.'))

        return out_lst

    def get_item_names(self):
        return self.data.keys()

    def _p_weight(self, row):
        return int(row[self.columns['p_weight']]) \
               if 'p_weight' in self.columns \
               else 1

    def _get_data(self, row_name: str, column_name: str):
        return self.data[row_name][self.columns[column_name]]