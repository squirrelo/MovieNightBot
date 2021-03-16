from setuptools import find_packages, setup

from movienightbot import __version__ as bot_version

requirements = ["discord-py>=1.3.4", "peewee", "marshmallow", "pyyaml", "imdbpy"]

test_requirements = ["pytest", "pytest-black", "pytest-flake8"]

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
