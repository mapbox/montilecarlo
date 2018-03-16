import os

from codecs import open as codecs_open
from setuptools import setup, find_packages


with codecs_open('README.md', encoding='utf-8') as f:
    long_description = f.read()


with open('montilecarlo/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            break

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='montilecarlo',
      version=version,
      description=u"Fancy Tile Sampling",
      long_description=long_description,
      classifiers=[],
      keywords='',
      author=u"Damon Burgett",
      author_email='damon@mapbox.com',
      url='https://github.com/mapbox/montilecarlo',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=read('requirements.txt').splitlines(),
      extras_require={
          'test': ['hypothesis', 'pytest'],
      })
