#!/bin/bash
echo "This will overwrite any existing matching conf files in /etc/supervisor/conf.d and /etc/nginx/sites-enabled"
read -p "Press enter to continue..."
echo "Copying Supervisor conf files"
cp -rf conf/supervisor/. /etc/supervisor/conf.d/
supervisorctl reread
supervisorctl update
cp -rf conf/nginx/. /etc/nginx/sites-enabled
cp -af conf/certs/. /etc/nginx/certs
echo "Copied Nginx conf"
service nginx restart