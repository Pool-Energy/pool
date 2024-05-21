import os

import setuptools
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pool",
    version="1.4.3",
    author="🌱 DJΞRFY 🚀",
    author_email="djerfy@gmail.com",
    description=("Pool.Energy of Chia blockchain."),
    license="AGPLv3",
    packages=setuptools.find_packages(),
    install_requires=["wheel", "chia-blockchain"],
    long_description=read("README.md"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: AGPL License",
    ],
)
