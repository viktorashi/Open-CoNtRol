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
FLASK_APP=open_control FLASK_ENV=development flask --debug run --host="$ip"
