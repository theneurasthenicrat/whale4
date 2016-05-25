#!/bin/sh

sed -e "s/'ENGINE': '[A-Za-z0-9\._]*'/'ENGINE': 'db engine here'/g;
s/'NAME': '[A-Za-z0-9\._]*'/'NAME': 'db name here'/g;
s/'USER': '[A-Za-z0-9\._]*'/'USER': 'db user here'/g;
s/'PASSWORD': '[A-Za-z0-9\._]*'/'PASSWORD': 'db password here'/g;
s/'HOST': '[A-Za-z0-9\._]*'/'HOST': 'db host here'/g"
