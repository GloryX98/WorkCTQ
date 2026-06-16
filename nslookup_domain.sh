#!/bin/bash

# Script: nslookup_domains.sh
# Usage: ./nslookup_domains.sh domains.txt

# Check if file is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <domain_list_file>"
    echo "Example: $0 domains.txt"
    exit 1
fi

DOMAIN_FILE="$1"

# Check if file exists
if [ ! -f "$DOMAIN_FILE" ]; then
    echo "Error: File '$DOMAIN_FILE' not found!"
    exit 1
fi

# Process each domain
echo "=== NSLOOKUP RESULTS ==="
echo ""

while IFS= read -r domain; do
    # Skip empty lines and comments
    if [ -z "$domain" ] || [[ "$domain" == \#* ]]; then
        continue
    fi
    
    echo "Domain: $domain"
    
    # Get the A record (IPv4 address)
    ip_address=$(nslookup "$domain" 2>/dev/null | grep -A1 "Name:" | grep "Address:" | awk '{print $2}')
    
    if [ -n "$ip_address" ]; then
        echo "  IP Address: $ip_address"
    else
        echo "  IP Address: Not found or domain doesn't exist"
    fi
    echo ""
done < "$DOMAIN_FILE"
