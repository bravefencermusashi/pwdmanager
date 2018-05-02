import datetime

import io

from pwdmanager.database import Database, DatabaseEntry
from abc import ABC, abstractmethod


class CommandException(Exception):
    def __init__(self, msg):
        self.msg = msg


class Command(ABC):

    @abstractmethod
    def perform_checks(self, database: Database):
        pass

    @abstractmethod
    def execute(self, database: Database):
        pass

    @abstractmethod
    def render(self, to_render):
        pass

    def check_execute_render(self, database: Database):
        self.perform_checks(database)
        res = self.execute(database)
        return self.render(res)


class AddEntry(Command):
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

        return entry

    def render(self, to_render):
        return 'entry with name {} successfully added to database'.format(to_render.name)


class ShowEntry(Command):
    def __init__(self, search):
        self.search = search

    def perform_checks(self, database: Database):
        if not self.search:
            raise CommandException('search cannot be empty')

    def render(self, entry: DatabaseEntry):
        if entry:
            repr = io.StringIO()
            repr.write('name: {}\n'.format(entry.name))
            repr.write('login: {}\n'.format(entry.login))
            if entry.login_alias:
                repr.write('login alias: {}\n'.format(entry.login_alias))
            repr.write('password: {}\n'.format(entry.pwd))
            if entry.aliases:
                repr.write('aliases: {}\n'.format(', '.join(entry.aliases)))
            if entry.tags:
                repr.write('tags: {}\n'.format(', '.join(entry.tags)))
            repr.write('creation date: {}\n'.format(entry.creation_date))
            repr.write('last update date: {}\n'.format(entry.last_update_date))

            res = repr.getvalue()
        else:
            res = ''

        return res

    def execute(self, database: Database):
        return database[self.search]


class ListEntries(Command):
    def __init__(self, search):
        self.search = search

    def perform_checks(self, database: Database):
        pass

    def execute(self, database: Database):
        return database.find_matching_entries(self.search)

    def minimal_repr(self, entry: DatabaseEntry):
        return 'name: {}\nlogin: {}\npassword: {}\n'.format(entry.name, entry.login, entry.pwd)

    def render(self, entry_list: list):
        if entry_list:
            repr = io.StringIO()
            repr.writelines(map(self.minimal_repr, entry_list))
            res = repr.getvalue()
        else:
            res = ''

        return res
