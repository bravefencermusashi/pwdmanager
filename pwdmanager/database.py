import abc
import json

import gnupg


class DataBaseCryptException(Exception):
    def __init__(self, msg):
        self.msg = msg


class SaveAndLoadInterceptor(abc.ABC):
    @abc.abstractmethod
    def at_save_time(self, plaintext: str):
        pass

    @abc.abstractmethod
    def at_load_time(self, loaded_bytes: bytes):
        pass


class EncodeInterceptor(SaveAndLoadInterceptor):
    def at_save_time(self, plaintext: str):
        return plaintext.encode()

    def at_load_time(self, loaded_bytes: bytes):
        return loaded_bytes.decode()


class PythonGnuPGCrypterInterceptor(SaveAndLoadInterceptor):
    def __init__(self, passphrase):
        self.passphrase = passphrase
        self.gpg = gnupg.GPG()

    def at_save_time(self, plaintext: str):
        return self.encrypt(plaintext)

    def encrypt(self, plaintext: str):
        result = self.gpg.encrypt(
            plaintext.encode(), [], passphrase=self.passphrase, symmetric=True
        )
        return result.data

    def at_load_time(self, loaded_bytes: bytes):
        return self.decrypt(loaded_bytes)

    def decrypt(self, to_decrypt: bytes):
        decrypt = self.gpg.decrypt(to_decrypt, passphrase=self.passphrase)
        if not decrypt.ok:
            raise DataBaseCryptException(decrypt.status)
        else:
            return decrypt.data.decode()


class DBLoader:
    def __init__(self, db_path: str, interceptor=None):
        self.db_path = db_path
        self.interceptor = interceptor if interceptor else EncodeInterceptor()

    @staticmethod
    def json_decode_database_entry(o):
        if "__db_entry__" in o:
            db_entry = DatabaseEntry(
                o["name"], o["login"], o["pwd"], o.get("login_alias")
            )
            db_entry.creation_date = o["creation_date"]
            db_entry.last_update_date = o["last_update_date"]
            db_entry.aliases = set(o.get("aliases", set()))
            db_entry.tags = set(o.get("tags", set()))
            return db_entry
        else:
            return o

    def load_db(self):
        with open(self.db_path, "rb") as db_file:
            db_dict = json.loads(
                self.interceptor.at_load_time(db_file.read()),
                object_hook=self.json_decode_database_entry,
            )
        return Database(db_dict)

    def save_db(self, db):
        to_be_written = self.interceptor.at_save_time(
            json.dumps(db, cls=DatabaseJSONEncoder)
        )
        with open(self.db_path, "wb") as db_file:
            db_file.write(to_be_written)


class DatabaseJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Database):
            return o.db
        elif isinstance(o, DatabaseEntry):
            res = {
                "__db_entry__": True,
                "name": o.name,
                "login": o.login,
                "pwd": o.pwd,
                "creation_date": o.creation_date,
                "last_update_date": o.last_update_date,
            }
            if o.aliases:
                res["aliases"] = list(o.aliases)
            if o.tags:
                res["tags"] = list(o.tags)
            if o.login_alias:
                res["login_alias"] = o.login_alias

            return res
        else:
            return json.JSONEncoder.default(self, o)


class DataBaseManager:
    def __init__(self, db_loader: DBLoader):
        self.db_loader = db_loader
        self.db = None

    def init_db(self):
        self.db = Database(dict())
        self.db_loader.save_db(self.db)
        return self.db

    def load_db(self):
        self.db = self.db_loader.load_db()
        return self.db

    def save_db(self):
        self.db_loader.save_db(self.db)

    def save_db_if_needed(self):
        saved = False
        if self.db.modified:
            self.save_db()
            saved = True

        return saved


def create_db_manager(db_path, db_password):
    return DataBaseManager(
        DBLoader(db_path, interceptor=PythonGnuPGCrypterInterceptor(db_password))
    )


class DatabaseEntry:
    def __init__(self, name, login, pwd, login_alias=None):
        self.name = name
        self.login = login
        self.login_alias = login_alias
        self.pwd = pwd
        self.aliases = set()
        self.tags = set()
        self.creation_date = None
        self.last_update_date = None


class Database:
    def __init__(self, db: dict = None):
        self.db = db if db is not None else dict()
        self.modified = False

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

    def __delitem__(self, key):
        result = self.__getitem__(key)
        if result:
            self.db.__delitem__(result.name)
            self.modified = True
        return bool(result)

    def __contains__(self, item):
        return self.__getitem__(item) is not None

    def add_entry(self, entry: DatabaseEntry):
        self.db[entry.name] = entry
        self.modified = True

    def find_matching_entries(self, name_or_alias_part, tag_part=None):
        return self.filter_with_tag_part(
            tag_part,
            self.filter_with_name_or_alias_part(name_or_alias_part, self.db.values()),
        )

    @staticmethod
    def filter_with_name_or_alias_part(name_or_alias_part, entries):
        if name_or_alias_part:
            name_or_alias_matching_entries = list()
            for entry in entries:
                if (
                    name_or_alias_part in entry.name
                    or Database.is_part_contained_in_items(
                        name_or_alias_part, entry.aliases
                    )
                ):
                    name_or_alias_matching_entries.append(entry)
        else:
            name_or_alias_matching_entries = entries

        return name_or_alias_matching_entries

    @staticmethod
    def filter_with_tag_part(tag_part, entries):
        if tag_part:
            result = list()
            for entry in entries:
                if Database.is_part_contained_in_items(tag_part, entry.tags):
                    result.append(entry)
        else:
            result = entries

        return result

    @staticmethod
    def is_part_contained_in_items(part, list_):
        for item in list_:
            if part in item:
                return True
        return False
