# Requisitos previos

- docker
- docker-compose
- Jinja 2

# Instalación de Docker

Referencia: https://docs.docker.com/engine/install/ubuntu/

- con usuario root

```bash
apt-get update

sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo apt-key fingerprint 0EBFCD88

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

apt-get update

#Instalar Docker
sudo apt-get install docker-ce docker-ce-cli containerd.io

#validar instalación
docker --version
```

- Instalación de docker-compose

Referencia: https://docs.docker.com/compose/install/

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

#modificar permisos para ejecuta
sudo chmod +x /usr/local/bin/docker-compose

#verificar instalación
docker-compose --version
```

# ODOO + NGINX

- Como sudo

```bash
sudo su
```

- crear directorio de trabajo

```bash
mkdir /opt/odoo
```

- NGINX Config

```bash
cd /opt/odoo/odoo-pos/nginx/nginx-config
j2 nginx_template.conf.j2 ../../env.json > nginx_template.conf
```

- ODOO Config

```bash
cd /opt/odoo/odoo-pos/config
j2 odoo.conf.j2 ../env.json > odoo.conf
```

- ODOO docker-compose

```bash
cd /opt/odoo/odoo-pos
j2 docker-compose.yml.j2 env.json > docker-compose.yml

docker-compose up -d --build
```
