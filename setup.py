from setuptools import setup, find_packages

setup(
    name="rings_network",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "eth-ape[recommended-plugins]",
        "pandas",
        "duckdb>=0.9.0",
        "click>=8.0.0",
        "python-dotenv>=0.19.0",
        "requests>=2.32.3",
    ],
    entry_points={
        'console_scripts': [
            'rings-sim=scripts.rings:cli',
        ],
    },
)