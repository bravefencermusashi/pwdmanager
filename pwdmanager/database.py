import json


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


def json_object_hook(o):
    if '__db_entry__' in o:
        db_entry = DatabaseEntry(o['name'], o['login'], o['pwd'], o.get('login_alias'))
        db_entry.creation_date = o['creation_date']
        db_entry.last_update_date = o['last_update_date']
        db_entry.aliases = o.get('aliases', list())
        db_entry.tags = o.get('tags', list())
        return db_entry
    else:
        return o


class DatabaseJSONEncoder(json.JSONEncoder):
    def default(self, o):
        default_encoding = json.JSONEncoder.default
        if isinstance(o, Database):
            return o.db
        elif isinstance(o, DatabaseEntry):
            res = {
                '__db_entry__': True,
                'name': o.name,
                'login': o.login,
                'pwd': o.pwd,
                'creation_date': o.creation_date,
                'last_update_date': o.last_update_date
            }
            if o.aliases:
                res['aliases'] = o.aliases
            if o.tags:
                res['tags'] = o.tags
            if o.login_alias:
                res['login_alias'] = o.login_alias

            return res
        else:
            return default_encoding(self, o)


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

    def find_matching_entries(self, item):
        if not item:
            matching_entries = list(self.db.values())
        else:
            matching_entries = list()
            for entry in self.db.values():
                if item in entry.name:
                    matching_entries.append(entry)
                else:
                    for alias in entry.aliases:
                        if item in alias:
                            matching_entries.append(entry)
                            break

        return matching_entries
