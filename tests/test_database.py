import database
from tests import helper


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
        entry = database.DatabaseEntry('test_name', None, None)
        db.add_entry(entry)
        assert len(db) == 1
        assert db['test_name'] == entry


def test_create_database_entry():
    json_repr = helper.create_full_json_repr()

    entry = database.create_database_entry(json_repr)
    assert entry.name == 'test_name'
    assert entry.login == 'test_login'
    assert entry.pwd == 'test_pwd'
    assert entry.login_alias == 'test_login_alias'
    assert entry.aliases == ['alias1', 'alias2']
    assert entry.tags == ['tag1', 'tag2']
    assert entry.creation_date == 'test_creation_date'
    assert entry.last_update_date == 'test_last_update_date'

    json_repr = helper.create_min_json_repr()

    entry = database.create_database_entry(json_repr)
    assert entry.login_alias is None
    assert entry.aliases == list()
    assert entry.tags == list()


def test_create_database():
    list = [helper.create_full_json_repr('1'), helper.create_min_json_repr('2')]
    db = database.create_database(list)
    assert len(db) == 2
    assert '1' in db
    assert type(db['1']) == database.DatabaseEntry
    assert '2' in db
    assert type(db['2']) == database.DatabaseEntry
