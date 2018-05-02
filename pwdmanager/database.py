def create_database(json_repr: list):
    return Database({entry.name: entry for entry in map(create_database_entry, json_repr)})


def create_database_entry(json_repr: dict):
    db_entry = DatabaseEntry(json_repr['name'], json_repr['login'], json_repr['pwd'])
    db_entry.login_alias = json_repr.get('login_alias', None)
    db_entry.aliases = json_repr.get('aliases', list())
    db_entry.tags = json_repr.get('tags', list())
    db_entry.creation_date = json_repr['creation_date']
    db_entry.last_update_date = json_repr['last_update_date']

    return db_entry


class DatabaseEntry:
    def __init__(self, name, login, pwd, login_alias=None):
        self.name = name
        self.login = login
        self.login_alias = login_alias
        self.pwd = pwd
        self.aliases = list()
        self.tags = list()
        self.creation_date = None
        self.last_update_date = None


class Database:
    def __init__(self, db: dict):
        self.db = db

    def __len__(self):
        return len(self.db)

    def __getitem__(self, item):
        result = self.db.get(item, None)

        if result is None:
            for entry in self.db.values():
                if item in entry.aliases:
                    result = entry
                    break

        return result

    def __contains__(self, item):
        return self.__getitem__(item) is not None

    def add_entry(self, entry: DatabaseEntry):
        self.db[entry.name] = entry
