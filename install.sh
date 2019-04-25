#!/bin/bash
echo "Python Environment Setup"
export $(grep -v '^#' .env | xargs)
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

read -p "Do you want to set up postgresql automatically from .env values? <y/N> " prompt
if [[ $prompt == "y" || $prompt == "Y" || $prompt == "yes" || $prompt == "Yes" ]]
then
  echo "Creating Postgresql Database ${DB_NAME} and User ${DB_USER}"
  sudo -u postgres ./conf/postgres.sh
else
    echo "Skipping Postgresql Setup"
fi

dpkg -s supervisor 2>/dev/null >/dev/null || sudo apt-get -y install supervisor
echo "This will overwrite any existing matching conf files in /etc/supervisor/conf.d and /etc/nginx/sites-enabled"
read -p "Press enter to continue..."
echo "Copying Supervisor conf files"
cp -af conf/supervisor/. /etc/supervisor/conf.d/
supervisorctl reread
supervisorctl update
dpkg -s nginx 2>/dev/null >/dev/null || sudo apt-get -y install nginx
cp -af conf/nginx/. /etc/nginx/sites-enabled
cp -af conf/certs/. /etc/nginx/certs
# todo: make it install to sites-available, then dynamically symlink by file name.. but thats too much for a sunday morning
echo "Copied Nginx conf"
service nginx restart

