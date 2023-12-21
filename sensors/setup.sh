cd ~
sudo apt install parallel
#write out current crontab
crontab -l > mycron
#echo new cron into cron file
echo "* * * * * /bin/bash ~/capture.sh >> ~/logs" >> mycron
#install new cron file
crontab mycron
rm mycron
