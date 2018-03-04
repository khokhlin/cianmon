from setuptools import setup, find_packages


setup(
    name='cianmon',
    version='1.1.0',
    description='Monitoring flat prices on the cian.ru website',
    url='https://github.com/khokhlin/cianmon',
    author='Andrey Khokhlin',
    author_email='khokhlin@gmail.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'bs4',
        'dateutils'
        ],
    entry_points={
        'console_scripts': [
            'cianmon=cianmon.main:main',
        ],
    },
)
