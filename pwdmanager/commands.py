import datetime
import io
from abc import ABC, abstractmethod

from pwdmanager.database import Database, DatabaseEntry


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
            raise CommandException("cannot have a name, login or password empty")

        if self.name in database:
            raise CommandException(
                "name {} already exists in database".format(self.name)
            )

        for alias in self.aliases:
            if alias in database:
                raise CommandException(
                    "alias {} already exists in database".format(alias)
                )

    def execute(self, database: Database):
        entry = DatabaseEntry(
            self.name, self.login, self.pwd, login_alias=self.login_alias
        )
        entry.aliases = self.aliases
        entry.tags = self.tags
        entry.creation_date = datetime.datetime.now().isoformat()
        entry.last_update_date = entry.creation_date

        database.add_entry(entry)

        return entry

    def render(self, to_render):
        return "entry with name {} successfully added to database".format(
            to_render.name
        )


class ShowEntry(Command):
    def __init__(self, search):
        self.search = search

    def perform_checks(self, database: Database):
        if not self.search:
            raise CommandException("search cannot be empty")

    def render(self, entry: DatabaseEntry):
        if entry:
            repr = io.StringIO()
            repr.write("name: {}\n".format(entry.name))
            repr.write("login: {}\n".format(entry.login))
            if entry.login_alias:
                repr.write("login alias: {}\n".format(entry.login_alias))
            repr.write("password: {}\n".format(entry.pwd))
            if entry.aliases:
                repr.write("aliases: {}\n".format(", ".join(entry.aliases)))
            if entry.tags:
                repr.write("tags: {}\n".format(", ".join(entry.tags)))
            repr.write("creation date: {}\n".format(entry.creation_date))
            repr.write("last update date: {}\n".format(entry.last_update_date))

            res = repr.getvalue()
        else:
            res = ""

        return res

    def execute(self, database: Database):
        return database[self.search]


class ListEntries(Command):
    def __init__(self, search, tag_part=None):
        self.search = search
        self.tag_part = tag_part

    def perform_checks(self, database: Database):
        if self.tag_part is not None and len(self.tag_part) == 0:
            raise CommandException("cannot search with an empty tag part")

    def execute(self, database: Database):
        return database.find_matching_entries(self.search, self.tag_part)

    def minimal_repr(self, entry: DatabaseEntry):
        return "name: {}\nlogin: {}\npassword: {}".format(
            entry.name, entry.login, entry.pwd
        )

    def render(self, entry_list: list):
        if entry_list:
            repr = io.StringIO()
            repr.write("\n\n".join(map(self.minimal_repr, entry_list)))
            res = repr.getvalue()
        else:
            res = "no match"

        return res


class RemoveEntry(Command):
    def __init__(self, name):
        self.name = name

    def perform_checks(self, database: Database):
        if not self.name:
            raise CommandException("cannot provide an empty name for removal")

    def execute(self, database: Database):
        return database.__delitem__(self.name)

    def render(self, was_removed: bool):
        if was_removed:
            return "the entry with name or alias {} has been removed".format(self.name)
        else:
            return (
                f"nothing removed since no entry has name "
                f"or alias equal to {self.name}"
            )


class UpdateEntry(Command):
    def __init__(self, name_or_alias):
        self.name_or_alias = name_or_alias
        self.add_aliases = list()
        self.rm_aliases = list()
        self.add_tags = list()
        self.rm_tags = list()
        self.pwd = None
        self.login = None
        self.login_alias = None

    def perform_checks(self, database: Database):
        if not self.name_or_alias:
            raise CommandException("cannot provide an empty name or alias for removal")

        if self.name_or_alias in database:
            for alias_to_add in self.add_aliases:
                if alias_to_add not in self.rm_aliases:
                    if alias_to_add in database:
                        raise CommandException(
                            "alias {} already exists in database".format(alias_to_add)
                        )

    def execute(self, database: Database):
        entry = database[self.name_or_alias]
        if entry:
            for alias_to_add in self.add_aliases:
                entry.aliases.add(alias_to_add)
            for alias_to_rm in self.rm_aliases:
                if alias_to_rm in entry.aliases:
                    entry.aliases.remove(alias_to_rm)

            for tag_to_add in self.add_tags:
                entry.tags.add(tag_to_add)
            for tag_to_rm in self.rm_tags:
                if tag_to_rm in entry.tags:
                    entry.tags.remove(tag_to_rm)

            if self.pwd:
                entry.pwd = self.pwd
            if self.login:
                entry.login = self.login
            if self.login_alias is not None:
                entry.login_alias = self.login_alias

            entry.last_update_date = datetime.datetime.now().isoformat()

            database.modified = True

            return True, entry.name
        else:
            return False, self.name_or_alias

    def render(self, to_render: tuple):
        if to_render[0]:
            return "entry with name {} was updated".format(to_render[1])
        else:
            return "no entry found with name or alias {}".format(to_render[1])
