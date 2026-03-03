#!/usr/bin/env python3
import os
import sys
import argparse
import requests

def get_zone_records(zone_id, api_token):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    params = {"type": "TXT"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()["result"]
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(
        description="Debug DNS TXT records"
    )
    parser.add_argument("domain", help="Domain name (e.g. ihostbanana.qzz.io)")
    parser.add_argument("zone_id", help="Cloudflare Zone ID")

    args = parser.parse_args()
    domain = args.domain
    zone_id = args.zone_id

    # Get credentials from environment variable
    api_token = os.getenv("CLOUDFLARE_API_TOKEN")
    if not api_token:
        print("Error: CLOUDFLARE_API_TOKEN environment variable not set")
        exit(1)

    # Fetch all DNS records
    print("Fetching all TXT records in the zone:")
    all_records = get_zone_records(zone_id, api_token)

    # Filter records matching our domain pattern
    matching_records = []
    for record in all_records:
        if domain in record["name"]:
            matching_records.append(record)

    print(f"All TXT records: {len(all_records)}")
    print(f"Matching records: {len(matching_records)}")

    # Check for meta record specifically
    meta_found = False
    for record in all_records:
        if record['name'] == f'meta.{domain}':
            print(f"\nFOUND META RECORD:")
            print(f"Name: {record['name']}")
            print(f"Content: {record['content']}")
            print(f"Content type: {type(record['content'])}")
            meta_found = True
            break

    if not meta_found:
        print("\nMETA RECORD NOT FOUND!")
        print("All TXT records in zone:")
        for record in all_records:
            print(f"Name: {record['name']}")

    print(f"\nMatching records:")
    for record in matching_records:
        print(f"Name: {record['name']}")

if __name__ == "__main__":
    main()
