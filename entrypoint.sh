#!/bin/bash

set -e

debug=$2

# set the postgres database host, port, user and password according to the environment
# and pass them as arguments to the odoo process if not present in the config file
: ${HOST:=${DB_PORT_5432_TCP_ADDR:='db'}}
: ${PORT:=${DB_PORT_5432_TCP_PORT:=5432}}
: ${USER:=${DB_ENV_POSTGRES_USER:=${POSTGRES_USER:='odoo'}}}
: ${PASSWORD:=${DB_ENV_POSTGRES_PASSWORD:=${POSTGRES_PASSWORD:='odoo'}}}

DB_ARGS=()

function check_config() {
    param="$1"
    value="$2"
    if grep -q -E "^\s*\b${param}\b\s*=" "$ODOO_RC" ; then
        value=$(grep -E "^\s*\b${param}\b\s*=" "$ODOO_RC" |cut -d " " -f3|sed 's/["\n\r]//g')
    fi;
    DB_ARGS+=("--${param}")
    DB_ARGS+=("${value}")
}

check_config "db_host" "$HOST"
check_config "db_port" "$PORT"
check_config "db_user" "$USER"
check_config "db_password" "$PASSWORD"

# if [[ "$2" == "dev" ]] ; then
# exec echo 10000 | tee /proc/sys/fs/inotify/max_user_watches
# fi

case "$1" in
    -- | odoo)
        shift
        if [[ "$1" == "scaffold" ]] ; then
            if [[ "$debug" == "dev" ]] ; then
                exec /usr/bin/python3 -m debugpy --listen 0.0.0.0:3001 /usr/bin/odoo
            else    
                exec odoo "$@"
            fi    
        else
            wait-for-psql.py ${DB_ARGS[@]} --timeout=30
            if [[ "$debug" == "dev" ]] ; then
                exec /usr/bin/python3 -m debugpy --listen 0.0.0.0:3001 /usr/bin/odoo "${DB_ARGS[@]}"
            else    
                exec odoo "$@" "${DB_ARGS[@]}"
            fi    
        fi
        ;;
    -*)
        wait-for-psql.py ${DB_ARGS[@]} --timeout=30
        if [[ "$debug" == "dev" ]] ; then
            exec /usr/bin/python3 -m debugpy --listen 0.0.0.0:3001 /usr/bin/odoo "${DB_ARGS[@]}"
        else 
            exec odoo "$@" "${DB_ARGS[@]}"
        fi
        ;;
    *)
        exec "$@"
esac

exit 1

