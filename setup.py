from setuptools import setup

setup(
    name='pwdmanager',
    version='1.0.0.dev1',
    packages=['pwdmanager'],
    entry_points={
        'console_scripts': ['pwdmanager = pwdmanager.pwdmanager:main']
    }
)
