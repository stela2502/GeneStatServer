from setuptools import setup, find_packages

# Read README.md for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

print(long_description)  # Add this to setup.py temporarily and run it

setup(
    name="GeneStatsServer",
    version="0.4.0",
    packages=find_packages(include=["GeneStatsServer", "GeneStatsServer.*"]),  # ✅ Include all submodules
    install_requires=[
        "Flask",  # or whatever your dependencies are
    ],
    package_data={
        "GeneStatsServer": [
            "utils/*",  # Explicitly include all files inside the utils folder
            "migrations/schema.sql", # the sql schema we need
            "templates/*", # the html templates
            "static/*", # nothing at the moment, but better save than sorry..

        ],
    },
    entry_points={
        "console_scripts": [
            "GeneStatsServer = GeneStatsServer.main:main",
        ],
    },
    author="Stefan Lang",
    author_email="Stefan.Lang@med.lu.se",
    url="https://github.com/stela2502/GeneStatServer",  # Your GitHub URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
