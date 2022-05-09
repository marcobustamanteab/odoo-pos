# Odoo POS CCU S.A.

Odoo POS es un sistema Multi-empresa, implementado con Odoo 14 Enterprise.
Se hace cargo de los procesos de:
* Ventas POS
* Contabilidad
* Inventario
* Clientes
* Facturación

Se implementa el estándar worldclass de P.O.S de Odoo y se adapata para que se integre con CCU y sus procesos.




# Instalación

## Características del SOftware

- Versión: Odoo 14 versión docker
- Lenguaje: Python 3.6
- BD: Postgres 10
- Arquitectura de Desarrollo: Framework Odoo ORM 


## Requisitos previos

- Postgres 10
- docker
- docker-compose 
- Jinja 2 Cli

## PASO 1: Librerías Adicionales para modulos externos y desarrollos

apt-get -y install python3-simplejson python3-cachetools python3-xmltodict python3-openssl 
pip3 install setuptools_rust signxml pdf417gen

## PASO 2: Instalación de Docker

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

- PASO 3: Instalación de docker-compose

Referencia: https://docs.docker.com/compose/install/

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

#modificar permisos para ejecuta
sudo chmod +x /usr/local/bin/docker-compose

#verificar instalación
docker-compose --version
```

## PASO 4: INSTALACIÓN DE ODOO

- Como sudo

```bash
sudo su
```

- crear directorio de trabajo

```bash
mkdir /opt/odoo
```

- clonar el repositorio
```
git clone http://gitlab.ccu.cl/odoo-pos/odoo-pos.git
```

- ajustar env.json según necesidad, si se requiere. 
- Variable "env" asignar "PROD", "QA" o "DEV" para ambientes de ejecución en servidor y "LOCAL" para ambiente local
```
nano env.json
```

- inicie la aplicación
```
./run.sh
```
