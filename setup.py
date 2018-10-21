from setuptools import setup, find_packages
from savannah import __email__, __author__, __uri__, __description__, __name__, __version__

setup(
    name=__name__,
    version=__version__,
    description=__description__,
    url=__uri__,
    author=__author__,
    author_email=__email__,
    packages=find_packages(),
    install_requires=[
        # These are the requisites for an official installation.
        # requirements.txt indicates requirements for testing and development.
        # 'networkx==2.1',
        # 'numpy==1.15.1',
        # 'pandas==0.23.4',
        # 'pyyaml==3.13',
    ],
    scripts=['bin/savannah', ],
    zip_safe=False)
