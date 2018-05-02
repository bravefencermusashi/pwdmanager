from setuptools import setup

setup(
    name='pwdmanager',
    version='0.0.1.dev1',
    packages=['pwdmanager'],
    entry_points={
        'console_scripts': ['pwdmanager = pwdmanager.pwdmanager:main']
    }
)
