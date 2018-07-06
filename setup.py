from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="asyncspider",
    version="0.0.1",
    description="Distributed web crawler based on uvloop, aiohttp and redis",
    long_description=long_description,
    url="https://github.com/xvzf/asyncspider",
    author="Matthias Riegler",
    author_email="matthias@xvzf.tech",

    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],

    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=["uvloop", "aioredis", "aiohttp", "yarl"],

    entry_points={
        "console_scripts": ["asyncspider = asyncspider.__main__:main"]
    },

    project_urls={  # Optional
        "Bug Reports": "https://github.com/xvzf/asyncspider/issues",
        "Source": "https://github.com/xvzf/asyncspider/",
    },

)
