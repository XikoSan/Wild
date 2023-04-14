container_name="wild_politics-wildpolitics-1"
container_dir="./app/locale"

# Получаем ID контейнера
container_id=$(docker ps -aqf "name=${container_name}")

# Проверяем, что получили ID
if [ "$container_id" == "" ]; then
  echo "Контейнер не найден"
  exit 1
fi

docker cp "${container_id}:${container_dir}" ./

cd /root/wild-politics

git checkout translations

git add *.po *.mo

git commit -m "Ночной бэкап"

git remote set-url origin https://M4TPOCKUN:ATBBuK9bT5se38ab65J3TJwunWKa9E498D89@bitbucket.org/M4TPOCKUN/wild-politics.git

git push origin translations

git checkout common-test