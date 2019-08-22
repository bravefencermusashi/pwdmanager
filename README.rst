==========
pwdmanager
==========

Keep your passwords safe and close

This is a command line tool to manage your passwords. Those are stored locally in an encrypted JSON formatted file. The
encryption and decryption is performed by GPG_. Passwords unlocking is done using a master password.

Benefits of using this program include :

- use difficult and different passwords to secure your accounts
- you don't have to trust third parties for storing your passwords : everything is stored locally
- provide high end and reliable encryption with GPG_
- it is open source : anybody can check the code

installation
------------

With pip or your favorite package manager::

    pip install pwdmanager
    pipenv install pwdmanager
    poetry add pwdmanager

That's it.

If you want to build the wheel yourself you have to have `poetry <https://poetry.eustace.io/>`_
installed. Then change directory to the root of the sources and issue::

    poetry build

Then you can install the wheel with your favorite package manager::

    pip install dist/pwdmanager-XXX-py3-none-any.whl
    pipenv install dist/pwdmanager-XXX-py3-none-any.whl
    poetry add pwdmanager --path=dist/pwdmanager-XXX-py3-none-any.whl

requirements
------------

You need to have GPG_ installed.

.. _GPG: https://gnupg.org/

database
--------

The database is a local JSON file. It is encrypted. At first usage it will be initialised. The default location is
``~/.pwddb`` but you can provide you own location.

concepts
--------

An entry in basically a container for an account information. The password database is a list of entries. An entry has
the following attributes:

name
    this is an id of the entry. Two entries cannot have the same name.

login
    account login

password
    account password

login alias
    a second or alternative account login

aliases
    one entry can have several aliases. Each alias is an id of the entry. Two entries cannot have the same alias.
    Useful to provide easier to match or remember names

tags
    one entry can have several tags. Useful to categorize entries. You can search with tags

creation date
    entry creation date. Immutable.

last update date
    obvious

usage
-----
::

    usage: pwdmanager [-h] [-d DATABASE] [-p MASTER_PASSWORD]
                        {add,show,list,rm,update} ...

    positional arguments:
      {add,show,list,rm,update}

    optional arguments:
      -h, --help            show this help message and exit
      -d DATABASE, --database DATABASE
                            specify where the database is located
      -p MASTER_PASSWORD, --master-password MASTER_PASSWORD
                            password to crypt and decrypt the database


There are 5 main commands:

add
    to add a new entry

show
    to list all the attributes of a particular entry, you have to give the exact name or alias of an entry

list
    to look for entries. Can be used without any parameter, in that case all entries will be listed. You can also provide
    a string, then all the entries with name or aliases containing this string will be listed. You can filter by tag also.

rm
    to remove an entry. No confirmation asked, be careful.

update
    to modify an entry

For all those commands, use the ``-h/--help`` flag to have details about parameters::

    pwdmanager add -h


be careful
----------

- Choose your master password wisely. Do not forget it or you won't be able to recover your database
- When adding a password you specify it in the command. Thus it may be stored in the shell history. Therefore I strongly
  recommend to clean your history after adding passwords. On linux ``sed -i /^pwdmanager/d ~/.bash_history`` will do the trick
  in most cases.
- When adding a password I recommend you surround it by single quotes because special characters may be interpreted
  by the shell
- back your password database up
