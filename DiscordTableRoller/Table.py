import csv
import asyncio
import random
import io
import posixpath

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
        if filepath in parents:
            raise RecursionError('Can not create a table containing itself')
        self.data = {}
        self.columns = {}
        self.aliases = []
        self.filepath = filepath
        self.recur = False
        self.out_of = 0
        
        with io.open(filepath, 'r', encoding='utf8') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read())
            csvfile.seek(0)
            contents = list(csv.reader(csvfile, dialect))

        if contents[0][0] == 'RECURSIVE':
            self.recur = True
        else:
            for alias in contents[0]:
                if alias != '':
                    container[alias] = self
                    self.aliases.append(alias)
        
        if parents != [] and not self.recur:
            raise RecursionError('Can not create a recursive table out of a root table')

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
                if contents[1][i] == 'recur':
                    row_lst.append(Table(normpath(posixpath.join(filepath,row[i]), \
                        parents=parents + [filepath])))
                else:
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
            out_lst.extend((": ",self.get(at,'brief')))
        if 'recur' in self.columns:
            out_lst.append("\n\t")
            out_lst.extend(self.get(at,'recur').roll())

        return out_lst

    def query(self, name: str, *args): 
        '''attempts to retrieve data on param name, all but the 
        brief & p_wieght if args is empty or attempts to 
        retrieve the data or item of a recusive table with the key args[0] if 
        either case fails it returns an error message

        :param name: the name of the object you are attempting to retrive
            type: string
        :param args: the names of the data or recursive table entries you are 
                     attempting to retrive. empty returns all but brief & p_weight
            type: tuple of string
        :return: a list of strings to be str.join()-ed before sent to discord
        '''
        out_lst = []

        if name in self.data:
            if args == ():
                out_lst.extend(('```\n',name,':\n'))
                for c_key in self.columns:
                    if c_key != 'p_weight'   \
                        and c_key != 'brief' \
                        and c_key != 'description' \
                        and c_key != 'recur':
                        out_lst.extend((c_key,': ',self.get(name, c_key),'\n'))

                if 'description' in self.columns:
                    out_lst.extend(('\n',self.get(name,'description')))
                elif 'brief' in self.columns:
                    out_lst.extend(('\n',self.get(name,'brief')))

                if 'recur' in self.columns:
                    out_lst.append('\n')
                    out_lst.extend(_p_rolls(name))
                out_lst.append('```')

            elif args[0] in self.columns:
                out_lst.extend(('```\n',name,':\n'))
                if args[0] != 'recur':
                    out_lst.extend((args[0],': ', self.get(name,args[0])))
                else:
                    out_lst.extend(_p_rolls(name))
                out_lst.append('```')
            elif 'recur' in self.columns and args[0] in self.get(name,'recur').data:
                out_lst.extend(('```\n',name,': '))
                out_lst.extend(self.get(name, 'recur').query(*args[1:])[1:])

            else:
                out_lst.extend(('','`',name,'` does not have any `', \
                    args[0],'`.'))
        else:
            out_lst.extend(('','`',name,'` is not an item in this table.'))

        return out_lst

    def get_item_names(self):
        return self.data.keys()

    def _p_weight(self, row):
        return int(row[self.columns['p_weight']]) \
               if 'p_weight' in self.columns \
               else 1

    def get(self, row_name: str, column_name: str):
        return self.data[row_name][self.columns[column_name]]

    def _p_rolls(self, row_name: str):
        out_lst=['Possible rolls:']
        for key in self.get(row_name,'recur').get_item_names():
            out_lst.extend((' \"',key,'\"'))
        return out_lst