#!/usr/bin/env python3
import os
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

# Get credentials from environment variable
api_token = os.getenv("CLOUDFLARE_API_TOKEN")
if not api_token:
    print("Error: CLOUDFLARE_API_TOKEN environment variable not set")
    exit(1)

zone_id = "f3bbd09735bd62d420381d21c282722d"

# Fetch all DNS records
print("Fetching all TXT records in the zone:")
all_records = get_zone_records(zone_id, api_token)

# Filter records matching our domain pattern
matching_records = []
for record in all_records:
    if "ihostbanana.qzz.io" in record["name"]:
        matching_records.append(record)

print(f"All TXT records: {len(all_records)}")
print(f"Matching records: {len(matching_records)}")

# Check for meta record specifically
meta_found = False
for record in all_records:
    if record['name'] == 'meta.ihostbanana.qzz.io':
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