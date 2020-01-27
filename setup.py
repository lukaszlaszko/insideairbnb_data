from setuptools import setup


setup(
    name='insideairbnb_data',
    version='0.0.0.9000',
    scripts=['download_airbnb.py'],
    install_requires = [
        'beautifulsoup4',
        'loguru',
        'pandas',
        'requests',
        'tqdm'
    ]
)
