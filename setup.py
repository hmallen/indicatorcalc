from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='indicatorcalc',
    version='0.1a1',
    author='Hunter M. Allen',
    author_email='allenhm@gmail.com',
    license='MIT',
    #packages=find_packages(),
    packages=['indicatorcalc'],
    #scripts=['bin/heartbeatmonitor.py'],
    install_requires=['numpy>=1.2.1',
                      'TA-Lib>=0.4.17'],
    description='Centralized, TA-Lib based technical analysis indicator calculation from json market data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hmallen/indicatorcalc',
    keywords=['indicator', 'calc'],
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
)
