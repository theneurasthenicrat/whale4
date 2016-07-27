
# Simple Makefile for Django project routines

directory = .
apps = accounts polls
models = accounts/models.py polls/models.py
settings = whale4/settings.py
settings-generic = whale4/settings-generic.py

clean:
	-rm -rf build
	-rm -rf *~*
	-find . -name '*.pyc' -exec rm {} \;

anonymize: $(settings)
	cat $(settings) |$(directory)/anonymize-settings.sh > $(settings-generic)

test: clean
	python3 $(directory)/manage.py test

pep8:
	pep8.py --filename=*.py --ignore=W --exclude="manage.py,settings.py" --statistics --repeat $(directory) 

pylint:
	pylint3 $(directory)  --max-public-methods=50 --include-ids=y --ignored-classes=Item.Meta --method-rgx='[a-z_][a-z0-9_]{2,40}$$'

fresh_syncdb: $(models)
	$(directory)/resetDB.sh
	find . -wholename "*/migrations/*.py" |xargs rm
	python3 $(directory)/manage.py makemigrations $(apps)
	python3 $(directory)/manage.py migrate

syncdb: $(models)
	python3 $(directory)/manage.py makemigrations $(apps)
	python3 $(directory)/manage.py migrate

shell: syncdb
	python3 $(directory)/manage.py shell

run: syncdb anonymize
	python3 $(directory)/manage.py runserver
