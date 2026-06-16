#!/usr/bin/env python3

import subprocess
import csv
import sys
import re

def nslookup_domain(domain):
    """Perform nslookup on a domain and return the second IP address"""
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
            if len(ip_addresses) >= 2:
                # Return the SECOND IP address (index 1)
                return ip_addresses[1]
            elif len(ip_addresses) == 1:
                # If only one IP exists, return that one
                return ip_addresses[0]
        return "Not found or domain doesn't exist"
            
    except subprocess.TimeoutExpired:
        return "Timeout error"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 nslookup_csv.py <input_domains_file> <output_csv_file>")
        print("Example: python3 nslookup_csv.py domains.txt results.csv")
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
        
        resolved = 0
        unresolved = 0
        
        for i, domain in enumerate(domains, 1):
            ip = nslookup_domain(domain)
            status = "Resolved" if ip and "Not found" not in ip and "Error" not in ip else "Not Resolved"
            
            if status == "Resolved":
                resolved += 1
            else:
                unresolved += 1
            
            writer.writerow([domain, ip, status])
            
            # Progress indicator
            print(f"[{i}/{len(domains)}] {domain} -> {ip}")
        
        # Add summary at the bottom
        writer.writerow([])
        writer.writerow(['Summary', '', ''])
        writer.writerow(['Total Domains', len(domains), ''])
        writer.writerow(['Resolved', resolved, ''])
        writer.writerow(['Not Resolved', unresolved, ''])
    
    print(f"\n✅ CSV file saved to: {output_file}")
    print(f"📊 Summary: Total={len(domains)}, Resolved={resolved}, Not Resolved={unresolved}")
    print(f"📝 Note: Using the SECOND IP address when available (falls back to first if only one exists)")

if __name__ == "__main__":
    main()
