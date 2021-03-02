# requisitos previos
- docker
- docker-compose
- Jinja 2

# ODOO

```bash
sudo su
```

# crear directorio de trabajo
```bash
mkdir /opt/odoo
```

# Habilitar PostgreSQL
```bash
cd /opt/odoo/odoo-pos/postgreSQL
j2 docker-compose.yml.j2 ../env.json > ./docker-compose.yml
docker-compose up -d
```

# NGINX Config
```bash
cd /opt/odoo/odoo-pos/nginx/nginx-config
j2 nginx_template.conf.j2 ../../env.json > nginx_template.conf
```

# ODOO Config
```bash
cd /opt/odoo/odoo-pos/config
j2 odoo.conf.j2 ../env.json > odoo.conf
```

# ODOO docker-compose
```bash
cd /opt/odoo/odoo-pos
j2 docker-compose.yml.j2 env.json > docker-compose.yml

docker-compose up -d --build
```