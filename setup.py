import os

from setuptools import setup, find_packages


def read_req(path):
    with open(path) as f:
        req = f.read().splitlines()
        req = [r for r in req if r and not r.startswith('#')]
        return req


ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
__VERSION__ = 'v0.1.8'


base_requires = read_req(os.path.join(ROOT, 'requirements', 'setup.txt'))
tests_requires = read_req(os.path.join(ROOT, 'requirements', 'development.txt'))


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
