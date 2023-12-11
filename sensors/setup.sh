cd ~
apt install parallel
#write out current crontab
crontab -l > mycron
#echo new cron into cron file
echo "* * * * * /bin/bash ~/capture.sh" >> mycron
#install new cron file
crontab mycron
rm mycron
