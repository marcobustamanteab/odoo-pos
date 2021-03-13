FROM wso2qa4.ccu.cl:5000/odoo:ccu_enterprise-14.0

COPY config             /etc/odoo
COPY src/custom-addons  /mnt/extra-addons/custom-addons

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]