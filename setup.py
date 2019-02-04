import os

from setuptools import setup, find_packages

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements


ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
__VERSION__ = 'v0.1.8'

base_requires = parse_requirements(os.path.join(ROOT, 'requirements', 'setup.txt'), session='hack')
base_requires = [str(item.req) for item in base_requires]

tests_requires = parse_requirements(os.path.join(ROOT, 'requirements', 'development.txt'), session='hack')
tests_requires = [str(item.req) for item in tests_requires]

setup(
    name="django-dde",
    version=__VERSION__,
    author="Stored",
    author_email="dev@stored.com.br",
    url="https://github.com/stored/django-dde",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    description='Asynchronous and Distributed Data Exporter from a Django QuerySet',
    long_description=open(os.path.join(ROOT, 'README.MD'), 'r', encoding='utf8').read(),
    install_requires=base_requires,
    setup_requires=base_requires,
    extras_require={
        'tests': tests_requires,
    },
    zip_safe=True,
    include_package_data=True,
)
