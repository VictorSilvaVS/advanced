"""
setup.py - Configuração de instalação para pysql_lite
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pysql_lite",
    version="1.2.0",
    author="Victor Silva",
    author_email="victorsilva139br@gmail.com",
    description="Mini-ORM leve para SQLite com Query Chaining e Zero Dependências",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VictorSilvaVS/pysql_lite",
    project_urls={
        "Bug Tracker": "https://github.com/VictorSilvaVS/pysql_lite/issues",
        "Documentation": "https://github.com/VictorSilvaVS/pysql_lite#documentação",
        "Source Code": "https://github.com/VictorSilvaVS/pysql_lite",
        "Changelog": "https://github.com/VictorSilvaVS/pysql_lite/blob/main/CHANGELOG.md",
    },
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    keywords="orm sqlite database lightweight zero-dependencies query-builder",
)
