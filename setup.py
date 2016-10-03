import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


VERSION = '0.0.1'
AUTHOR_NAME = 'Adam Erispaha'
AUTHOR_EMAIL = 'aerispaha@gmail.com'

install_requires = [
    'hhcalcs',
    'pandas',
    ]

setup(name='rrsim',
      version=VERSION,
      description='Tools for simulating the efficacy of a infrastructure renew and replacement program',
      author=AUTHOR_NAME,
      url='https://github.com/aerispaha/rrsim',
      author_email=AUTHOR_EMAIL,
      packages=find_packages(exclude=('tests')),
      install_requires=install_requires,
      long_description=read('README.rst'),
      platforms="OS Independent",
      license="MIT License",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
      ]
)
