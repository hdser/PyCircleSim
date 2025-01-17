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
        "jinja2>=3.1.5",
        "black>=24.10.0",
        "colorama==0.4.6",
        "panel>=1.3.0",         
        "holoviews>=1.18.0",    
        "param>=2.0.0",         
        "bokeh>=3.3.0",  
        "hvplot>=0.11.2",
    ],
    entry_points={
        'console_scripts': [
            'rings-sim=scripts.rings:cli',
            'sim-explorer=app.app:main',
        ],
    },
)