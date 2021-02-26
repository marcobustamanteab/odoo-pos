FROM odoo:14.0

# Set default user when running the container
USER root

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN apt-get update \
        && apt-get install -y --no-install-recommends \
            python3-cachetools

# Install python libraries for base rest
RUN python3 -m pip install --force-reinstall pip setuptools
RUN python3 -m pip install --force-reinstall pip python3-openssl

RUN ["chmod", "+x", "/entrypoint.sh"]
RUN ["chmod", "+x", "/usr/local/bin/wait-for-psql.py"]
