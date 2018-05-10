from setuptools import setup

setup(
    name='pwdmanager',
    version='1.0.0rc1',
    packages=['pwdmanager'],
    entry_points={
        'console_scripts': ['pwdmanager = pwdmanager.pwdmanager:main']
    },
    install_requires=['python-gnupg']
)
