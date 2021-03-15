FROM wso2qa4.ccu.cl:5000/odoo:ccu_enterprise-14.0

# Set default user when running the container
#USER root

COPY config             /etc/odoo
COPY src/custom-addons  /mnt/extra-addons/custom-addons

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/odoo/odoo.log \
    && ln -sf /dev/stderr /var/log/odoo/odoo.log

RUN set -x \
    && sed -ri \
    -e 's!^(\s*odoo)\s+\S+!\1 /proc/self/fd/1!g' \
    -e 's!^(\s*odoo)\s+\S+!\1 /proc/self/fd/2!g' \
    "/var/log/odoo"    

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]