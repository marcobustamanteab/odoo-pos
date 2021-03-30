rm -rf logs
j2 Dockerfile.j2 env.json > Dockerfile
j2 docker-compose.yml.j2 env.json > docker-compose.yml
docker-compose up -d