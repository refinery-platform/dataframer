import os
from os.path import abspath, dirname, join, normpath

# isort has different behavior for different versions of python here.
import yaml  # isort:skip
from setuptools import find_packages, setup  # isort:skip

with open(join(dirname(__file__), 'README.md')) as f:
    readme_md = f.read()

# allow setup.py to be run from any path
os.chdir(normpath(join(abspath(__file__), os.pardir)))

version = open(join('dataframer', 'VERSION.txt')).read().strip()
travis = yaml.load(open('.travis.yml').read())

python_classifiers = ['Programming Language :: Python :: {}'.format(v)
                      for v in travis['python']]
assert len(python_classifiers) > 0

setup(
    name='dataframer',
    version=version,
    install_requires=[
        'pandas'
    ],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    license='MIT License',
    description='Load any file into a pandas DataFrame, with a minimum of '
                'configuration, and a focus on bioinformatics',
    long_description=readme_md,
    long_description_content_type='text/markdown',
    url='https://github.com/refinery-platform/dataframer/',
    author='Chuck McCallum',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'] + python_classifiers,
    zip_safe=False
    # TODO: This fixes "ValueError: bad marshal data (unknown type code)"
    # ... but I don't understand why it broke, or whether this is a good fix.
)
