import csv
import asyncio
import random
import io
#import posixpath
import os.path as path

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
            #dialect = csv.Sniffer().sniff(csvfile.read())
            csvfile.seek(0)
            contents = list(csv.reader(csvfile))

        if contents[0][0] == 'RECURSIVE':
            self.recur = True
        else:
            for alias in contents[0]:
                if alias != '':
                    container[alias] = self
                    self.aliases.append(alias)

        if parents == [] and self.recur:
            return

        if parents != [] and not self.recur:
            raise RecursionError('Can not create a recursive table out of a root table')

        columns_index = 0
        used_columns = []
        for i in range(len(contents[1])):
            if contents[1][i] == 'name':
                name_index = i
            elif contents[1][i] != '':
                self.columns[contents[1][i]] = columns_index
                used_columns.append(i)
                columns_index += 1

        for row in contents[2:]:
            if row[name_index] == 'SKIP':
                continue
            row_lst = []
            for i in used_columns:
                if contents[1][i] == 'recur':
                    row_lst.append(Table(\
                        path.normpath(path.join( \
                            path.dirname(filepath),row[i])), \
                        parents=parents + [filepath]))
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
        for key in self.data:
            total += self._p_weight(self.data[key])
            if loc < total:
                at = key
                break

        out_lst = [at]
        if 'brief' in self.columns:
            out_lst.extend((": ",self.get(at,'brief')))
        if 'recur' in self.columns:
            out_lst.append("\n\t")
            out_lst.extend(self.get(at,'recur').roll())

        return out_lst

    def query(self, name: str, datum_name = None, *rcrsv_call_data): 
        '''attempts to retrieve data on param name, all but the 
        brief & p_wieght if args is empty or attempts to 
        retrieve the data or item of a recusive table with the key args[0] if 
        either case fails it returns an error message

        :param name: the name of the object you are attempting to retrive
            type: string
        :param datum_name: the name of the data or recursive table entry you are 
                     attempting to retrive. None returns all but brief & p_weight
            type: string
        :param rcrsv_call_data: the first item will be used as datum_name in
                                recursive calls to this method, think lisp
        :return: a list of strings to be str.join()-ed before sent to discord
        '''
        out_lst = []

        if name in self.data:
            if datum_name is None:
                out_lst.extend(('```\n',name,':\n'))
                for c_key in self.columns:
                    if c_key not in ['p_weight','brief','description','recur']:
                        out_lst.extend((c_key,': ',self.get(name, c_key),'\n'))

                if 'description' in self.columns:
                    out_lst.extend(('\n',self.get(name,'description')))
                elif 'brief' in self.columns:
                    out_lst.extend(('\n',self.get(name,'brief')))

                if 'recur' in self.columns:
                    out_lst.append('\n')
                    out_lst.extend(self._p_rolls(name))
                out_lst.append('```')

            elif datum_name in self.columns:
                out_lst.extend(('```\n',name,':\n'))
                if datum_name != 'recur':
                    out_lst.extend((datum_name,': ', self.get(name,datum_name)))
                else:
                    out_lst.extend(self._p_rolls(name))
                out_lst.append('```')
            elif 'recur' in self.columns and datum_name in self.get(name,'recur').data:
                out_lst.extend(('```\n',name,': '))
                out_lst.extend(self.get(name, 'recur').query(datum_name,*rcrsv_call_data)[1:])

            else:
                out_lst.extend(('','`',name,'` does not have any `', \
                    datum_name,'`.'))
        else:
            out_lst.extend(('','`',name,'` is not an item in this table.'))

        return out_lst

    def get_item_names(self):
        return self.data.keys()

    def _p_weight(self, row):
        '''takes a row and returns the probability weight for to that row'''
        return int(row[self.columns['p_weight']]) \
               if 'p_weight' in self.columns      \
               else 1

    def get(self, row_name: str, column_name: str):
        '''Returns the value of the cell in the column_name column and the
        row_name row raises an exception if the cell does not exist.'''
        return self.data[row_name][self.columns[column_name]]

    def _p_rolls(self, row_name: str):
        '''returns a list of strings of the form ['Possible rolls:',' "',
key1,'"',' "',key1,'"', etc] for the recursive table in row 
row_name. If there is no recursive table it raises an 
exception.'''
        out_lst=['Possible rolls:']
        for key in self.get(row_name,'recur').get_item_names():
            out_lst.extend((' \"',key,'\"'))
        return out_lst