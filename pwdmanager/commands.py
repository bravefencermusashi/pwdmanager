import datetime

from database import Database, DatabaseEntry


class CommandException(Exception):
    def __init__(self, msg):
        self.msg = msg


class CreateEntry:
    def __init__(self, name, login, pwd, login_alias=None):
        self.name = name
        self.login = login
        self.login_alias = login_alias
        self.pwd = pwd
        self.aliases = list()
        self.tags = list()

    def perform_checks(self, database: Database):
        if not self.name or not self.login or not self.pwd:
            raise CommandException('cannot have a name, login or password empty')

        if self.name in database:
            raise CommandException('name {} already exists in database'.format(self.name))

        for alias in self.aliases:
            if alias in database:
                raise CommandException('alias {} already exists in database'.format(alias))

    def execute(self, database: Database):
        entry = DatabaseEntry(self.name, self.login, self.pwd, login_alias=self.login_alias)
        entry.aliases = self.aliases
        entry.tags = self.tags
        entry.creation_date = datetime.datetime.now().isoformat()
        entry.last_update_date = entry.creation_date

        database.add_entry(entry)

    def check_and_execute(self, database: Database):
        self.perform_checks(database)
        self.execute(database)
