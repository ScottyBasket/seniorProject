echo
echo Site is live. Do not wipe out director any longer
echo



cd /Users/eli/git/eli
rsync -rav * root@apps.owls.plus:/home/dua/9202-intramural/
echo 
echo 
echo  Clean migrations on server before you do systemctl restart apache2 !!!!
echo 
