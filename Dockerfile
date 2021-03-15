FROM wso2qa4.ccu.cl:5000/odoo:ccu_enterprise-14.0

# Set default user when running the container
USER odoo

COPY config             /etc/odoo
COPY src/custom-addons  /mnt/extra-addons/custom-addons

# forward request and error logs to docker log collector
RUN ln -sf /proc/1/fd/1 /var/log/odoo/odoo.log

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]