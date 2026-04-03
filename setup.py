from setuptools import find_packages, setup

from movienightbot import __version__ as bot_version

requirements = [
    "discord-py>=2.7.1",
    "peewee",
    "marshmallow",
    "pyyaml",
    "imdbinfo>=0.8.2",
]

test_requirements = [
    "pytest",
    "pytest-asyncio",
    "dpytest>=0.6",
    "ruff",
]

with open("README.rst") as f:
    long_description = f.read()

setup(
    name="movienight-bot",
    version=bot_version,
    license="WTFPL",
    description="Movie night suggestion and voting bot for Discord",
    long_description=long_description,
    author="Joshua Shorenstein",
    author_email="squirrelo@gmail.com",
    packages=find_packages(),
    package_data={
        "": [
            "webfiles/*.html",
            "webfiles/*.ico",
            "webfiles/**/*.png",
            "webfiles/**/*.css",
            "webfiles/**/*.js",
        ],
    },
    python_requires='>=3.9',
    install_requires=requirements,
    tests_require=test_requirements,
    extras_require={"test": test_requirements},
)
