#!/usr/bin/env python3

import sys
import subprocess
import json

VARS = {
    "web": [
        "allowed-hosts",
        "secret-key",
        "frontend-sentry-dsn",
        "sentry-dsn",
        "sentry-environment",
        "google-analytics-property-id",
    ],
    "nginx": [
        "fqdn",
        "certbot-email",
    ],
}


def get_secret(vault_name, name):
    resp = subprocess.check_output([
        "az", "keyvault", "secret", "show",
        "--vault-name", vault_name,
        "--name", name,
    ])
    return json.loads(resp)["value"]


def main(vault_name, service):
    for name in VARS[service]:
        env_var = name.upper().replace("-", "_")
        value = get_secret(vault_name, name)
        print(f'{env_var}={value}')

if __name__ == "__main__":
    [vault_name, service] = sys.argv[1:]
    main(vault_name, service)
