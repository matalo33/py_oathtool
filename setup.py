"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='py_oathtool',
    version='1.0.2',
    description='A python wrapper around oathtool',
    long_description=long_description,
    url='https://github.com/matalo33/py_oathtool',
    author='Matthew Taylor',
    author_email='matthew@m-taylor.co.uk',
    license='GPLv2',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Security',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='oathtool wrapper',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['subprocess32', 'pyaml'],

    entry_points={
        'console_scripts': [
            'otp = py_oathtool.otp:main',
        ],
    },
)
