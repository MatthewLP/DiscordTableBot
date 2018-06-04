'''Defines the WithOPs_mixin class for adding OP functionality and decorators to a class'''
class WithOPs_mixin(object):
    """Has Everything needed to take care of having OPs and a name for an object"""

    def __init__(self, author_id, name):
        super().__init__()
        self.OPs = {author_id:True} #True = curator, False = not
        self.name = name

    def is_op(func):
        '''Checks that the user who called this function is an OP, if not, an error
message will be returned as a list of strings
The first argument of the decorated function must represent a user id string.'''
        def wraper(self, *args, **kwargs):
            if args[0] in self.OPs:
                return func(self, *args, **kwargs)
            return ['You do not have permission to access ', self.name, '.']

        return wraper

    def is_curator(func):
        '''Checks that the person who called this function is the curator, if not, an error
message will be returned as a list of strings
The first argument of the decorated function must represent a user id string.'''
        def wraper(self, *args, **kwargs):
            if self.OPs.get(args[0], False):
                return func(self, *args, **kwargs)
            return ['You do not have permission to access ', self.name, ' in this way.']

        return wraper

    def bool_is_curator(self, user_id):
        return self.OPs.get(user_id, False)

    def bool_is_op(self, user_id):
        return user_id in self.OPs

    @is_op
    def push_op(self, caller_id, new_op_id):
        '''Adds new_op_id to the list of OPs for this object'''
        self.OPs[new_op_id] = False
        out_lst = ['<@', new_op_id, '> is now an OP for ', self.name]
        return out_lst

    @is_op
    def pop_op(self, caller_id, un_op_id):
        '''Attempts to remove un_op_id from the list of OPs for this object'''
        if un_op_id in self.OPs:
            if not self.OPs[un_op_id]:
                self.OPs.pop(un_op_id, False)
                out_lst = ['<@', un_op_id, '> is no longer an OP.']
            else:
                out_lst = ['You can not deOP the curator of this object.']
        else:
            out_lst = ['<@', un_op_id, '> is not an OP.']
        return out_lst

    @is_curator
    def migrate_curator(self, caller_id, new_curator_id):
        '''Moves the curator title from the current curator to new_curator_id.'''
        self.OPs[new_curator_id] = True
        self.OPs[caller_id] = False
        out_lst = ['<@', new_curator_id, '> is now the curator of ', self.name, '.']
        return out_lst

    is_op = staticmethod(is_op)
    is_curator = staticmethod(is_curator)
