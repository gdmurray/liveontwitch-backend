#!/bin/bash
if [ "$1" != "" ]; then
    echo "There is a config Specified $1"
    CONF=$1
else
    CONF=dev
    echo "There is no config Specified, default dev"
fi
echo "Python Environment Setup"
export $(grep -v '^#' .env | xargs)
sudo apt-get install build-essential python3-dev libpq-dev python3-pip python-pip
sudo -H pip3 install --upgrade virtualenv --quiet
if [[ ! -d "venv" ]]; then
    echo "Creating Virtual Environment"
    virtualenv -p python3 venv
fi
source venv/bin/activate
echo "Installing Packages"
pip3 install -r requirements.txt --quiet
echo "Installing and setting up Postgresql"
dpkg -s postgresql 2>/dev/null >/dev/null || sudo apt-get -y install postgresql postgresql-contrib
dpkg -s supervisor 2>/dev/null >/dev/null || sudo apt-get -y install supervisor
echo "This will overwrite any existing matching conf files in /etc/supervisor/conf.d and /etc/nginx/sites-enabled"
read -p "Press enter to continue..."
echo "Copying Supervisor conf files"
cp -af conf/${CONF}/supervisor/. /etc/supervisor/conf.d/
supervisorctl reread
supervisorctl update
dpkg -s nginx 2>/dev/null >/dev/null || sudo apt-get -y install nginx
cp -af conf/${CONF}/nginx/. /etc/nginx/sites-enabled
cp -af conf/${CONF}/certs/. /etc/nginx/certs
# todo: make it install to sites-available, then dynamically symlink by file name.. but thats too much for a sunday morning
echo "Copied Nginx conf"
service nginx restart

