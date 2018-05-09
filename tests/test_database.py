import json
from unittest.mock import MagicMock

import pytest

from pwdmanager import database


class TestDatabase:

    def test_len(self):
        db = database.Database(dict())
        assert len(db) == 0
        entry = database.DatabaseEntry('test_name', None, None)
        db.db['entry'] = entry
        assert len(db) == 1
        del (db.db['entry'])
        assert len(db) == 0

    def test_get_item_contains(self):
        db = database.Database(dict())
        assert db['test_name'] is None
        assert 'test_name' not in db
        entry = database.DatabaseEntry('test_name', None, None)
        db.db['test_name'] = entry
        assert db['test_name'] == entry
        assert 'test_name' in db

        assert db['alias'] is None
        assert 'alias' not in db
        entry.aliases = ['alias']
        assert db['alias'] == entry
        assert 'alias' in db

        assert db['alias2'] is None
        assert 'alias2' not in db
        entry.aliases.append('alias2')
        assert db['alias2'] == entry
        assert 'alias2' in db

    def test_add_entry(self):
        db = database.Database(dict())
        assert len(db) == 0
        assert not db.modified
        entry = database.DatabaseEntry('test_name', None, None)
        db.add_entry(entry)
        assert len(db) == 1
        assert db.modified
        assert db['test_name'] == entry

    def test_find_matching_entries(self):
        db = database.Database(dict())
        assert not db.find_matching_entries('st')
        entry_1 = database.DatabaseEntry('test_name', None, None)
        db.add_entry(entry_1)
        entry_2 = database.DatabaseEntry('toto', None, None)
        db.add_entry(entry_2)

        matching_items = db.find_matching_entries(None)
        assert len(matching_items) == 2
        assert entry_1 in matching_items and entry_2 in matching_items

        matching_items = db.find_matching_entries('')
        assert len(matching_items) == 2
        assert entry_1 in matching_items and entry_2 in matching_items

        matching_items = db.find_matching_entries('st')
        assert len(matching_items) == 1
        assert entry_1 in matching_items

        matching_items = db.find_matching_entries('t')
        assert len(matching_items) == 2
        assert entry_1 in matching_items and entry_2 in matching_items

        assert not db.find_matching_entries('lol')
        entry_1.aliases.append('ololo')
        matching_items = db.find_matching_entries('lol')
        assert len(matching_items) == 1
        assert entry_1 in matching_items


class TestDatabaseJSONEncoder:

    def test_default(self):
        json_encoder = database.DatabaseJSONEncoder()
        empty_dict = dict()
        db = database.Database(empty_dict)
        assert json_encoder.default(db) == empty_dict

        entry = database.DatabaseEntry('name', 'login', 'mdp', 'login_alias')
        entry_as_dict = json_encoder.default(entry)

        assert isinstance(entry_as_dict, dict)
        assert entry.name == entry_as_dict['name']
        assert entry.login == entry_as_dict['login']
        assert entry.pwd == entry_as_dict['pwd']
        assert entry.login_alias == entry_as_dict['login_alias']
        assert entry.creation_date == entry_as_dict['creation_date']
        assert entry.last_update_date == entry_as_dict['last_update_date']
        with pytest.raises(KeyError):
            entry_as_dict['aliases']
        with pytest.raises(KeyError):
            entry_as_dict['tags']

        entry.aliases = ['alias']
        entry.tags = ['tags']

        entry_as_dict = json_encoder.default(entry)
        assert entry.aliases == entry_as_dict['aliases']
        assert entry.tags == entry_as_dict['tags']


class TestPythonGnuPGCrypter:

    def test_encrypt_decrypt(self):
        crypter = database.PythonGnuPGCrypterInterceptor('pass')
        secret = 'secret'
        encrypted_secret = crypter.encrypt(secret)
        assert isinstance(encrypted_secret, bytes)
        assert encrypted_secret.decode() != secret

        decrypted_secret = crypter.decrypt(encrypted_secret)
        assert isinstance(decrypted_secret, str)
        assert decrypted_secret == secret

        crypter.passphrase = 'wrongpass'
        with pytest.raises(database.DataBaseCryptException):
            crypter.decrypt(encrypted_secret)


class TestDBLoader:

    def test_json_decode_database_entry(self):
        entry_as_json = {
            'name': 'name',
            'login': 'login',
            'pwd': 'pwd',
            'creation_date': 'creation_date',
            'last_update_date': 'last_update_date'
        }
        assert database.DBLoader.json_decode_database_entry(entry_as_json) == entry_as_json

        entry_as_json['__db_entry__'] = True
        entry = database.DBLoader.json_decode_database_entry(entry_as_json)
        assert type(entry) == database.DatabaseEntry
        assert entry.name == entry_as_json['name']
        assert entry.login == entry_as_json['login']
        assert entry.pwd == entry_as_json['pwd']
        assert entry.aliases == list()
        assert entry.tags == list()
        assert entry.login_alias is None
        assert entry.creation_date == entry_as_json['creation_date']
        assert entry.last_update_date == entry_as_json['last_update_date']

        entry_as_json['aliases'] = ['alias']
        entry_as_json['tags'] = ['tag']

        entry = database.DBLoader.json_decode_database_entry(entry_as_json)
        assert entry.aliases == entry_as_json['aliases']
        assert entry.tags == entry_as_json['tags']

    def test_load_db(self, tmpdir):
        db_file = tmpdir.join('database')
        db_as_dict = {
            'name': {
                '__db_entry__': True,
                'name': 'name',
                'login': 'login',
                'pwd': 'pwd',
                'creation_date': 'creation_date',
                'last_update_date': 'last_update_date'
            }
        }

        db_file.write_binary(json.dumps(db_as_dict).encode())
        db_loader = database.DBLoader(db_file.strpath)
        db = db_loader.load_db()
        assert len(db) == 1
        entry = db['name']
        assert entry.name == db_as_dict['name']['name']
        assert entry.login == db_as_dict['name']['login']
        assert entry.pwd == db_as_dict['name']['pwd']

    def test_save_db(self, tmpdir):
        db_file = tmpdir.join('database')
        db_loader = database.DBLoader(db_file.strpath)
        db = database.Database(dict())
        entry = database.DatabaseEntry('name', 'login', 'pwd')
        db.add_entry(entry)

        db_loader.save_db(db)
        db_as_dict = json.loads(db_file.read_binary().decode())
        assert 'name' in db_as_dict
        entry_as_dict = db_as_dict['name']
        assert entry_as_dict['name'] == entry.name
        assert entry_as_dict['login'] == entry.login
        assert entry_as_dict['pwd'] == entry.pwd


class TestDataBaseManager:

    @pytest.fixture(name='db_manager')
    def db_manager_fixture(self):
        return database.DataBaseManager(MagicMock(spec=database.DBLoader))

    def test_init_db(self, db_manager):
        db = db_manager.init_db()
        assert len(db) == 0
        assert db_manager.db == db
        assert db_manager.db_loader.save_db.call_count == 1

    def test_load_db(self, db_manager):
        db_manager.db_loader.load_db.return_value = 'db'
        db = db_manager.load_db()
        assert db == db_manager.db_loader.load_db.return_value
        assert db_manager.db == db_manager.db_loader.load_db.return_value

    def test_save_db(self, db_manager):
        db = database.Database({'key': 'value'})
        db_manager.db = db
        db_manager.save_db()
        db_manager.db_loader.save_db.assert_called_with(db)

    def test_save_db_if_needed(self, db_manager):
        db = database.Database({'key': 'value'})
        assert not db.modified
        db_manager.db = db
        assert not db_manager.save_db_if_needed()
        assert not db_manager.db_loader.save_db.called
        db.modified = True
        assert db_manager.save_db_if_needed()
        assert db_manager.db_loader.save_db.called
