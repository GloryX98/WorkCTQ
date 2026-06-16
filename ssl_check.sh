#!/bin/bash
# ssl_check.sh - Check SSL certs on ALL ports for a list of IPs using nmap
# Usage: ./ssl_check.sh <ip_list_file>
 
IP_FILE="${1}"
TODAY=$(date +%Y-%m-%dT%H:%M:%S)
 
NO_CERT="no_cert.txt"
EXPIRED="expired_cert.txt"
VALID="valid_cert.txt"
 
if [[ -z "$IP_FILE" || ! -f "$IP_FILE" ]]; then
    echo "Usage: $0 <ip_list_file>"
    exit 1
fi
 
# Clear output files
> "$NO_CERT"
> "$EXPIRED"
> "$VALID"
 
echo "Starting SSL check on ALL ports | Today: $TODAY"
echo "------------------------------------------------------"
 
while IFS= read -r IP || [[ -n "$IP" ]]; do
    # Skip empty lines and comments
    [[ -z "$IP" || "$IP" == \#* ]] && continue
 
    echo "[SCANNING] $IP ..."
 
    # Scan all 65535 ports, only open ones, grab ssl-cert script output
    RESULT=$(nmap -p- --script ssl-cert --open -T4 --min-parallelism 50 "$IP" 2>/dev/null)
 
    # Extract all "Not valid after" lines with their port context
    # nmap output groups by port, so we parse port + date together
    FOUND_ANY_CERT=0
 
    # Get all port/ssl-cert blocks: capture port number and its Not valid after
    while IFS= read -r LINE; do
        if [[ "$LINE" =~ ^([0-9]+)/tcp ]]; then
            CURRENT_PORT="${BASH_REMATCH[1]}"
        fi
        if [[ "$LINE" =~ [Nn]ot\ valid\ after ]]; then
            NOT_AFTER=$(echo "$LINE" | grep -oP '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
            [[ -z "$NOT_AFTER" ]] && continue
            FOUND_ANY_CERT=1
            if [[ "$NOT_AFTER" < "$TODAY" ]]; then
                echo "[EXPIRED]  $IP:$CURRENT_PORT  (expired: $NOT_AFTER)"
                echo "$IP:$CURRENT_PORT  |  expired: $NOT_AFTER" >> "$EXPIRED"
else
                echo "[VALID]    $IP:$CURRENT_PORT  (valid until: $NOT_AFTER)"
                echo "$IP:$CURRENT_PORT  |  valid until: $NOT_AFTER" >> "$VALID"
            fi
        fi
    done <<< "$RESULT"
 
    if [[ "$FOUND_ANY_CERT" -eq 0 ]]; then
        echo "[NO CERT]  $IP"
        echo "$IP" >> "$NO_CERT"
    fi
 
done < "$IP_FILE"
 
echo "------------------------------------------------------"
echo "Done."
echo "  No cert  : $NO_CERT   ($(wc -l < "$NO_CERT") hosts)"
echo "  Expired  : $EXPIRED ($(wc -l < "$EXPIRED") entries)"
echo "  Valid    : $VALID   ($(wc -l < "$VALID") entries)"
