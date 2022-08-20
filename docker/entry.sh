#! /bin/bash

# Bash "strict mode", to help catch problems and bugs in the shell
# script. Every bash script you write should include this. See
# http://redsymbol.net/articles/unofficial-bash-strict-mode/ for
# details.
set -euo pipefail

# cron runs from a non-interactive, non-login shell, so we inject
# env variables for cron here. https://stackoverflow.com/a/41938139
printenv > /etc/environment

cron -f
