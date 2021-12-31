FROM wso2qa4.ccu.cl:5000/pos-odoo-img:2.0.0

# Set default user when running the container

#USER root

COPY config             /etc/odoo
COPY src/custom-addons  /mnt/extra-addons/custom-addons

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/odoo/odoo.log

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
