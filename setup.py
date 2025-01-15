import os
import setuptools

from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pool",
    version="1.6.13",
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
