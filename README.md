# whale4 *WHich ALternative is Elected*

Whale4 is a free web project which is based on voting poll. There are two types of poll: open and secret ballots.
For each poll, the users are invited to vote and they can see the results.

Requirements
------------

- python >= 2.7
- django >= 1.8
- [django-bootstrap3] (https://github.com/dyve/django-bootstrap3)
- pycrypto

Getting Started
---------------

1. Edit ``whale4/settings.py`` for your database
2. Create database: ``python manage.py  makemigrations`` and then ``python manage.py migrate``
3. Run the server: ``python manage.py runserver``
4. Open website in browser at ``http://localhost:8000/`` 
