
#sets the environment variables for the flask app
#used as a external tool for the .run

#!/bin/bash

# List of interfaces to check
interfaces=("en0" "ens33" "ens37")

# Loop through each interface and get the IP address
for interface in "${interfaces[@]}"; do
  ip=$(ifconfig "$interface" 2>/dev/null | grep 'inet ' | awk '{print $2}')

  # If an IP address was found, break the loop
  if [ -n "$ip" ]; then
    echo "Using interface $interface with IP address $ip"
    break
  fi
done

# Check if an IP was found; if not, exit with an error
if [ -z "$ip" ]; then
  echo "No IP address found on specified interfaces (en0, ens33, ens37)."
  exit 1
fi

# Run the Flask application
#TODO sa faci o chestie sa poti sa pui argument de --debug la scriptu asta daca sa dea sau nu cu debug ca sa nu se mai zica ca da de ce sa vede asa cu eroriile alea cand dau run si doar daca vrei tu flagu sa-l pui

# shellcheck disable=SC2034
FLASK_RUN_HOST="$ip"
FLASK_DEBUG=1
FLASK_ENV=development
FLASK_RUN_PORT=5000
FLASK_APP=open_control
