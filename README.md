Whale4 (WHich ALternative is Elected)
=============================

Whale4 is a web application dedicated to collective decision making
and every day life voting. It should help you to choose collectively
amongst several alternatives. For that you can create a poll (open or
sealed ballots), tell people to vote, and visualize the results.

Whale4 allows you to choose amongst several preference expression
modes (ordinal, qualitative, approval, numerical), and is based on
[voting theory](https://en.wikipedia.org/wiki/Voting_theory) to
enlighten your decision.

Whale4 is a [free](http://www.fsf.org/) project: you can download the
source code and use it as you wish to (see license).

Whale4 can be used directly from the web application page. However,
you can download the source code (modify it if you want) and install
an instance of the application wherever you want. This page is
dedicated to people who want to do that.

License
-------

Whale4 is released under the [General Public License, version 3](https://github.com/theneurasthenicrat/whale4/blob/master/LICENSE).

Requirements
------------

- python >= 2.7
- django >= 1.8
- [django-bootstrap3](https://github.com/dyve/django-bootstrap3)
- pycrypto
- GNU gettext (for translation matters)
- A Database Management System (for instance Postgres) and its
  corresponding Python library (for instance ``psycopg2``)

Getting Started
---------------

1. Copy ``whale4/secret_settings_generic.py`` to
   ``whale4/secret_settings.py`` (``cp secret_settings_generic.py
   secret_settings.py``)

2. Complete ``whale4/secret_settings.py`` with the settings concerning
   persistance, email server, and secret key (for data encryption).

3. Run the application using ``make run``

4. Open the application in a web browser at ``http://localhost:8000/`` 

Complete installation example under Debian GNU/Linux
---------------

### Installing A Postgres Database

#### Install Postgres

    sudo apt-get postgresql

#### Create User and Database

There are different ways of creating users and databases with Postgres
(see [the Postgres documentation](http://www.postgresql.org/docs/current/static/) for more
information). In any case, you will have to connect to your postgres
cluster as a postgres user. Usually, if you do not know the password
of this user, you can proceed as follows:

1. First, connect as root: ``sudo -s``

2. Then connect as postgres user: ``su - postgres``

3. Finally run Postgres client: ``psql``
	
When you are connected, you can create a DB user using the following
SQL command:

    CREATE USER whale4 WITH ENCRYPTED PASSWORD '*********';

Then you can create the database using the following SQL command:

    CREATE DATABASE whale4 OWNER whale;

Finally, you can test that your are able to connect to this database
as follows:

1. log out from the database (type Ctrl-D or \q)

2. log in as follows: ``psql -U whale4 -d whale4``

### Installing Python3 and the required libraries

If Python3 is not installed in your machine, install it (together with
pip3, which will be needed to install some libraries):

    sudo apt-get install python3 python3-pip
	
You will also need the following packages (that you can install with
apt-get or another package manager like pip for instance):

    sudo apt-get install python3-django python3-crypto gettext

NB: It is possible that the version of Django that comes with your
distribution is older 1.8, in which case, some parts of the
application will not run. If it is the case, install django using the
PyPI package manager.

If you plan to use Postgres as DBMS, also install:

    sudo apt-get install python3-psycopg2	

This one is not in the packages of standard GNU/Linux distributions
but can be install using pip:

    sudo pip3 install django-bootstrap3

### Configuring application parameters

As explained above, before running the application, you will have to
configure its parameters.

First, copy ``whale4/secret_settings_generic.py`` to ``whale4/secret_settings.py`` (``cp secret_settings_generic.py  secret_settings.py``)

Then, complete ``whale4/secret_settings.py`` with the settings
concerning  persistance, email server, and secret key (for data
encryption).

Here is an example of settings that can be used to configure a
Postgres DB connection:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'whale4',
            'USER': 'whale',
            'PASSWORD': '0lds.ef!',
            'HOST': 'localhost',
            'PORT': '5432' # (change according to your server settings)
        }
    }

(Do not forget to complete the other parts of the file as well)

### Running the application

To run the application, type

    make run
	
Then, open the application in a web browser at
``http://localhost:8000/``.

### Running the application using WSGI behind Apache

Install the WSGI module for Apache2:

    sudo apt-get install libapache2-mod-wsgi-py3
	
If necessary, enable the WSGI module for Apache2:

    sudo a2enmod wsgi

Then, configure Apache to interpret your application using the WSGI
module, using [this documentation page](https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/modwsgi/)
for instance.

As a matter of example, you can create a file called
``/etc/apache2/sites-available/whale4.conf`` and put the following
configuration statements:

    WSGIScriptAlias /whale4 /var/www/whale4/whale4/wsgi.py
    WSGIPythonPath /var/www/whale4
    
    Alias /static/ /var/www/whale4/polls/static/
    
    <Directory /var/www/whale4/polls/static>
            Require all granted
    </Directory>
    
    <Directory /var/www/whale4/whale4>
            <Files wsgi.py>
                    Require all granted
            </Files>
    </Directory>

Then you can enable the site using:

    sudo a2ensite whale4
	
Finally restart your Apache2 server using:

	sudo service apache2 restart

And your application should be accessible using the following URL:
http://yourserver.yourdomain/whale4/
