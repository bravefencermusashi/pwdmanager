import argparse
import json
import os

from pwdmanager.commands import AddEntry, ShowEntry, ListEntries
from pwdmanager.database import Database, json_object_hook, DatabaseJSONEncoder


def create_arg_parser():
    parser = argparse.ArgumentParser(prog="password manager")
    parser.add_argument('-d', '--database', default=get_default_db_location())
    subparser = parser.add_subparsers(dest='command')
    subparser.required = True

    subparser_add = subparser.add_parser('add')
    subparser_add.add_argument('name')
    subparser_add.add_argument('login')
    subparser_add.add_argument('password')
    subparser_add.add_argument('-a', '--alias', nargs='+')
    subparser_add.add_argument('-t', '--tags', nargs='+')
    subparser_add.add_argument('--login-alias')

    subparser_show = subparser.add_parser('show')
    subparser_show.add_argument('name')

    subparser_list = subparser.add_parser('list')
    subparser_list.add_argument('search', nargs='?')

    return parser


def get_default_db_location():
    return os.path.join(os.path.expanduser('~'), '.pwddb')


def load_db(path):
    if not os.path.exists(path):
        db_dict = dict()
    else:
        with open(path, 'r') as db_file:
            db_dict = json.load(db_file, object_hook=json_object_hook)

    return Database(db_dict)


def save_db(path, database: Database):
    with open(path, 'w') as db_file:
        json.dump(database, db_file, cls=DatabaseJSONEncoder, indent=4)


def create_addentry_command(args):
    command = AddEntry(args.name, args.login, args.password, args.login_alias)
    if args.alias:
        command.aliases = args.alias
    if args.tags:
        command.tags = args.tags

    return command


def create_showentry_command(args):
    return ShowEntry(args.name)


def create_listentries_command(args):
    return ListEntries(args.search)


def main():
    parser = create_arg_parser()
    args = parser.parse_args()

    if args.command == 'add':
        command = create_addentry_command(args)
    elif args.command == 'show':
        command = create_showentry_command(args)
    elif args.command == 'list':
        command = create_listentries_command(args)

    db = load_db(args.database)
    print(command.check_execute_render(db))
    if db.modified:
        save_db(args.database, db)


if __name__ == '__main__':
    main()
