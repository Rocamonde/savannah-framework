from setuptools import setup
from savannah import __email__, __author__, __uri__, __description__, __name__, __version__

setup(name=__name__,
      version=__version__,
      description=__description__,
      url=__uri__,
      author=__author__,
      author_email=__email__,
      packages=[
          'savannah',
      ],
      install_requires=[
          'pandas', 'numpy', 'networkx'
      ],
      zip_safe=False)
