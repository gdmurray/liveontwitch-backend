#!/bin/bash
if [ "$1" != "" ]; then
    echo "There is a config Specified $1"
    CONF=$1
else
    CONF=dev
    echo "There is no config Specified, default dev"
fi
echo "This will overwrite any existing matching conf files in /etc/supervisor/conf.d and /etc/nginx/sites-enabled"
read -p "Press enter to continue..."
echo "Copying Supervisor conf files"
cp -rf conf/${CONF}/supervisor/. /etc/supervisor/conf.d/
supervisorctl reread
supervisorctl update
cp -rf conf/${CONF}/nginx/. /etc/nginx/sites-enabled
cp -af conf/${CONF}/certs/. /etc/nginx/certs
echo "Copied Nginx conf"
service nginx restart