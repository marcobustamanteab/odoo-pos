rm -rf logs
j2 config/odoo.conf.j2 env.json  > config/odoo.conf
j2 docker-compose.yml.j2 env.json > docker-compose.yml
docker-compose up --build -d 