class TableProfile():
    """Contains a collection of table locations and preloaded tables that can be loaded
or unloaded from the bot with one command. Also has a list of OPed accounts that can
modify the profile. With an option that only OPs can load it (Default off)."""

    def __init__(self, bot, op):
        self.bot = bot
        self.OPs = {op:True}
        self.loaders = {}
        self.tables = []
        self.table_names = []

    def add_op(ctx):
        stuff