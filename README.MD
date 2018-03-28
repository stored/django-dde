# Django Distributed Exporter (DDE)
> Asynchronous and Distributed Data Exporter from a Django QuerySet

DDE main goal is to get data from a QuerySet and export to an output format (currently CSV 
only) using Celery for task distribution.

## Installation

```sh
pip install django-dde
```

## Requirements

DDE uses **Celery** to manage its tasks. Currently our broker defaults to **Redis** so be
sure to install the dependencies need, 
[for more information click here.](http://docs.celeryproject.org/en/latest/getting-started/brokers/redis.html)

File management is dealt using Django's Default Storage. [For more information on how to use it
please click here.](https://docs.djangoproject.com/en/2.0/topics/files/#file-storage)

We developed DDE using **Django 1.11** and **Python 3.5**. Other versions are pending tests. Let us know
if works in your virtual environment.


## Usage

First of all:

`pip install django-dde`

Excelent! Now you must ensure that in your `settings.py` you have these configurations:

```python
EXPORTER_FROM_EMAIL = 'sender@email.com'
```

Now you have to configure a periodic task using Celery, [please refere to this link.](http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html)

Now in the code:

```python
from exporter.models import Exporter

exporter = Exporter.objects.create_exporter(
    queryset=Model.objects.queryset, # Change Model to your Model
    email=example@mail.com, # E-mail that will receive the link to the exporter,
    limit_per_task=100, # How many entries each task will proccess
)
```

And that's it! Simple, right?

## Development setup

Installing our dependencies in your virtual environment is pretty straight foward:

`pip install -r requirements/development.txt`

But you can use our Docker to test DDE. This method already install all dependencies
 on a container, creates a Redis container and you ready to go. We already configured some shortcuts to help:

```sh
make build # Builds docker image, be sure to run this first
make build-no-cache # Build/Rebuilds (cleaning cache) docker image

make tests # Run all tests
make bash # Enters Docker's Bash

make help # Shows the available commands
```

## Release History

* 0.1
    * Initial version

## Meta

Stored E-commerce

Distributed under the MIT license. See ``LICENSE`` for more information.

[https://github.com/stored](https://github.com/stored)

## Contributing

1. Fork it (<https://github.com/yourname/yourproject/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

*Remember: Every feature created or fixed must have a test written and/or fixed.*
