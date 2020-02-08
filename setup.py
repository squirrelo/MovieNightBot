from setuptools import find_packages, setup

from movienightbot import __version__ as botveresion

requirements = ["discord", "peewee", "marshmallow", "pyyaml"]

test_requirements = ["pytest", "pytest-black", "pytest-flake8"]

with open("README.rst") as f:
    long_description = f.read()

setup(
    name="movienight-bot",
    version=botveresion,
    license="BSD",
    description="Movie night suggestion and voting bot for Discord",
    long_description=long_description,
    author="Joshua Shorenstein",
    author_email="squirrelo@gmail.com",
    packages=find_packages(),
    install_requires=requirements,
    tests_require=test_requirements,
)
