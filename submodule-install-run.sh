git submodule sync
git submodule update --init
docker-compose down
docker-compose up --build -d