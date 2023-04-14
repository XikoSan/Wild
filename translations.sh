docker-compose cp wildpolitics:./app/locale ./

cd /root/wild-politics

git checkout translations

git add *.po *.mo

git commit -m "Ночной бэкап"

git remote set-url origin https://M4TPOCKUN:ATBBuK9bT5se38ab65J3TJwunWKa9E498D89@bitbucket.org/M4TPOCKUN/wild-politics.git

git push origin translations

git checkout common-test