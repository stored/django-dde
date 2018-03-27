import os

from setuptools import setup, find_packages

from pip.req import parse_requirements

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
__VERSION__ = '1.0.1'

base_requires = parse_requirements(os.path.join(ROOT, 'requirements', 'setup.txt'), session='hack')
base_requires = [str(item.req) for item in base_requires]

tests_requires = parse_requirements(os.path.join(ROOT, 'requirements', 'development.txt'), session='hack')
tests_requires = [str(item.req) for item in tests_requires]

setup(
    name="Django Distributed Exporter",
    version=__VERSION__,
    author="Stored",
    author_email="dev@stored.com.br",
    url="https://github.com/stored/django-dde",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    description='Empiricus CRM',
    long_description=open(os.path.join(ROOT, 'README.md'), 'r', encoding='utf8').read(),
    install_requires=base_requires,
    setup_requires=base_requires,
    extras_require={
        'tests': tests_requires,
    },
    zip_safe=True,
    include_package_data=True,
)
