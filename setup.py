from setuptools import find_packages, setup

from movienightbot import __version__ as bot_version

requirements = [
    "py-cord[speed]>=2.0",
    "peewee",
    "marshmallow",
    "pyyaml",
    "cinemagoer>=2022.12.27",
]

test_requirements = [
    "pytest",
    "pytest-asyncio",
    "pytest-black",
    "pytest-flake8",
    "dpytest>=0.5.1",
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
        ]
    },
    install_requires=requirements,
    tests_require=test_requirements,
    extras_require={"test": test_requirements},
)
