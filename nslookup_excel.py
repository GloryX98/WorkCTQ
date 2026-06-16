#!/usr/bin/env python3

import subprocess
import csv
import sys
import re
from datetime import datetime

def nslookup_domain(domain):
    """Perform nslookup on a domain and return the IP address"""
    try:
        result = subprocess.run(['nslookup', domain], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        
        if result.returncode != 0:
            return "Not found or domain doesn't exist"
        
        # Parse the IP address from the output
        ip_pattern = r'Address:\s*([\d.]+|[\da-fA-F:]+)'
        matches = re.findall(ip_pattern, result.stdout)
        
        if matches:
            # Filter out the DNS server address (usually ends with #53)
            ip_addresses = [ip for ip in matches if '#' not in ip]
            if ip_addresses:
                # If multiple IPs, join them with semicolon
                return '; '.join(ip_addresses)
        return "Not found or domain doesn't exist"
            
    except subprocess.TimeoutExpired:
        return "Timeout error"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 nslookup_excel.py <input_domains_file> <output_csv_file>")
        print("Example: python3 nslookup_excel.py domains.txt results.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Ensure output file has .csv extension
    if not output_file.endswith('.csv'):
        output_file += '.csv'
    
    try:
        with open(input_file, 'r') as file:
            domains = [line.strip() for line in file if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found!")
        sys.exit(1)
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['Hostname', 'IP Address', 'Status'])
        
        print(f"\nProcessing {len(domains)} domains...")
        print("-" * 60)
        
        for i, domain in enumerate(domains, 1):
            ip = nslookup_domain(domain)
            status = "Resolved" if ip and "Not found" not in ip and "Error" not in ip else "Not Resolved"
            
            writer.writerow([domain, ip, status])
            
            # Progress indicator
            print(f"[{i}/{len(domains)}] {domain} -> {ip}")
    
    print(f"\n✅ Results saved to: {output_file}")
    print(f"📊 You can open this file in Excel, LibreOffice Calc, or any spreadsheet software")

if __name__ == "__main__":
    main()
