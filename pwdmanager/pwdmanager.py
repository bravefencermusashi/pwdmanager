import argparse
import getpass
import os

from pwdmanager.commands import AddEntry, ShowEntry, ListEntries
from pwdmanager.database import create_db_manager, DataBaseCryptException


def create_arg_parser():
    parser = argparse.ArgumentParser(prog="password manager")
    parser.add_argument('-d', '--database', default=get_default_db_location())
    parser.add_argument('-p', '--master-password', help='password to crypt and decrypt database')
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

    master_pwd = args.master_password
    if not master_pwd:
        master_pwd = getpass.getpass()

    if args.command == 'add':
        command = create_addentry_command(args)
    elif args.command == 'show':
        command = create_showentry_command(args)
    elif args.command == 'list':
        command = create_listentries_command(args)

    db_manager = create_db_manager(args.database, master_pwd)
    try:
        db = db_manager.load_db() if os.path.exists(args.database) else db_manager.init_db()
    except DataBaseCryptException as e:
        print('database cannot be loaded : {}'.format(str(e)))
    else:
        print(command.check_execute_render(db))
        db_manager.save_db_if_needed()


if __name__ == '__main__':
    main()
