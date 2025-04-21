from setuptools import setup, find_packages

setup(
    name="oracle-script-executor",
    version="1.1",
    packages=find_packages(),
    install_requires=[
        "cx_Oracle==8.3.0",
    ],
    entry_points={
        'console_scripts': [
            'oracle-script-executor=src.main:main',
        ],
    },
) 