# Odoo POS CCU S.A.

Odoo POS es un sistema implementado con Odoo 14 Enterprise.
Se hace cargo de los procesos de:
* Ventas POS
* Contabilidad
* Inventario
* Clientes 

Se implementa el estándar worldclass de P.O.S de Odoo y se adapata para que se integre con CCU y sus procesos.


# Propiedades del Sistemas (checklist de recepción IDS)

| Requisito   |      Respuesta      |  Info adicional |
|-------------|---------------------|----------------:|
| Subgerencia Funcional |  V&D |  |
| Jefe de Proyecto |    Carlos Ugalde/Rafael Ramirez   |    |
| RTO | 2 horas |     |
| RPO | 2 horas ||
| ES SOX | Sí
| Impacta EEFF | Sí
| ES sistema crítico | Sí
| Utiliza relay de correso | Sí | ccurelay.ccu.cl
| Horario de Operación | lunes a domingo de 10:00 a 21:00
| Política de Respaldos | 1 vez al día en server Docker - respaldo cada una hora de la maquina host
| Existen reglas de firewall | No
| Utiliza SSL | Sí
| Existe balanceo en F5 | No



# Bases de Datos

| Tipo   |      Detalle      |  nombre de BD |
|-------------|---------------------|----------------:|
| POSTGRESQL |  Base de Datos principal del sistemasistema | MASTER

# Integración de Sistemas con Microservicios

| Tipo   |      Detalle      |  nombre de BD |
|-------------|---------------------|----------------:|
| API Contabilidad SAP |  Base de Datos principal del sistemasistema | [API Contabilidad](https://wiki-desarrollo.ccu.cl/books/apis/page/api-contabilidad-sap---versi%C3%B3n-sincrona)
| API Inventarios SAP |  Base de Datos principal del sistemasistema | [API Inventarios](https://wiki-desarrollo.ccu.cl/books/apis/page/api-inventario-sap---versi%C3%B3n-sincrona)

# Monitoreo del Sistema

| Tipo   |      Detalle      |  accesos |
|-------------|---------------------|----------------:|
| Grafana |  monitoreo de los docker y microservicios que componen el sistema | [Grafana](http://wsoprapp-lfj-03.ccu.cl:3000) |
| Kibana |  monitoreo y análisis de transacciones y logs | [Kibana](http://wsoprapp-lfj-03.ccu.cl:5602/app/discover) |
| Jaeger |    Monitoreo en linea de transacciones HTTP de Microservicios  |  [Jaeger](http://wsoprapp-lfj-04.ccu.cl:16686/jaeger)  |
| Portainer |  Visualización de docker y estado de ejecución | [Portainer](http://wsoprapp-lfj-04.ccu.cl:9000/#/containers) |



# DRP y Pruebas de Carga
| Requisito   |      Respuesta      |  Info adicional |
|-------------|---------------------|----------------:|
| Plan DRP |  Plan descrito en enlace  | [enlace](https://docs.google.com/document/d/1JPNsVB7oVNEvIAI6ev0pdcMtV1kix2t-MuMjbZ9tMeY/edit) |
| ¿Prueba DRP realizada |    Sí
| Validado por |    Felipe Ugarte   
| Requiere Pruebas de Carga | Sí
| ¿Pruebas de Carga realizadas? | Sí | [enlace](https://docs.google.com/document/d/1JPNsVB7oVNEvIAI6ev0pdcMtV1kix2t-MuMjbZ9tMeY/edit) |
# Niveles de Soporte y Escalamiento

## lunes a viernes de 8:30 a 17:30)
| N1   |      N2      |  N3 |
|-------------|---------------------|----------------:|
| Juan Perez +56 9 1234 5678 mail@ccu.cl | Jose Arándano +56 9 1234 5678 mail@ccu.cl  |  Amelia Cárdenas +56 9 1234 5678 mail@ccu.cl  |

## lunes a viernes de 17:30 a 08:29 y fines de semana
| N1   |      N2      |  N3 |
|-------------|---------------------|----------------:|
| Juan Perez +56 9 1234 5678 mail@ccu.cl | Jose Arándano +56 9 1234 5678 mail@ccu.cl  |  Amelia Cárdenas +56 9 1234 5678 mail@ccu.cl  |


# Sistemas Relacionados

| Sistema   |      Alcance      |  Info adicional |
|-------------|---------------------|----------------:|
| SAP |  Se integra en Contabilidad e Inventarios | - |
| Xerox |  Se integra con facturador Xerox | dte-xerox.ccu.cl  |
| FTP TRUCK LVT |  FS de libro de venta TRUCK |   |

# Diagrama de la Arquitectura del SIstema
![Image text](http://gitlab.ccu.cl/dclaver/template_ids/raw/master/diagramaPOS.png)


# URL's asociadas

| Descripción   |      URL      |  Info adicional |
|-------------|---------------------|----------------:|
| POS Producción | https://pos.ccu.cl | - |
| Xerox | dte-xerox.ccu.cl  |
| FTP TRUCK LVT |  FS de libro de venta TRUCK |   |

# Ambiente de QA

| Descripción   |      URL      |  Info adicional |
|-------------|---------------------|----------------:|
| POS QA | https://odooventas-qa.ccu.cl/ | BD: PRODQA, USR: admin, PASS: admin |

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
