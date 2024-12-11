from setuptools import setup, find_packages

setup(
    name="rings_network",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "eth-ape[recommended-plugins]",
        "pandas",
    ],
)