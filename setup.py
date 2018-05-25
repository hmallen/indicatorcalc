from setuptools import setup, find_packages

setup(
    name='indicatorcalc',
    version='0.1a',
    author='Hunter M. Allen',
    author_email='allenhm@gmail.com',
    license='MIT',
    #packages=find_packages(),
    packages=['indicatorcalc'],
    #scripts=['bin/heartbeatmonitor.py'],
    install_requires=['numpy>=1.2.1',
                      'TA-Lib>=0.4.17'],
    description='Centralized, TA-Lib based technical analysis indicator calculation from json market data',
    keywords=['indicator', 'calc'],
)
