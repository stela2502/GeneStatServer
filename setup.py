from setuptools import setup, find_packages

setup(
    name="GeneStatsServer",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "Flask",  # or whatever your dependencies are
    ],
    entry_points={
        "console_scripts": [
            "start-server = GeneStatsServer.main:GeneStatsServer",
        ],
    },
)