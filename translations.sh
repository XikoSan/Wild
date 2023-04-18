container_name="wild-politics_wildpolitics_1"
container_dir="./app/locale"

cd /root/wild-politics

git checkout translations

container_id=$(docker ps -aqf "name=${container_name}")

if [ "$container_id" == "" ]; then
  echo "Container not found"
  exit 1
fi

docker cp "${container_id}:${container_dir}" ./

git pull -f

git add *.po *.mo

git commit -m "Night backup"

git remote set-url origin https://M4TPOCKUN:ATBBuK9bT5se38ab65J3TJwunWKa9E498D89@bitbucket.org/M4TPOCKUN/wild-politics.git

git push origin translations

git checkout common-test