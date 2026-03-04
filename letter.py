import os
import sys
import base64
import hashlib
import argparse
import requests
import json
#this function gets the hash of a file
def get_sha256(file_path):
    """Compute SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        # read in chunks cuz big files
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

# encode the data to base64
def encode_data(data):
    """Encode binary data into URL-safe base64"""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

# split data into chunks for DNS
def chunk_data(data, chunk_size=200):
    """Split encoded data into chunks"""
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunks.append(data[i:i + chunk_size])
    return chunks

# get all the DNS records we care about
def get_zone_records(zone_id, api_token, domain_pattern):
    """Fetch all DNS records matching the pattern."""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    params = {"type": "TXT", "per_page": 100}

    all_records = []

    try:
        while True:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            records = data["result"]

            # find records that match our pattern
            for record in records:
                if domain_pattern in record["name"]:
                    all_records.append(record)

            # check if there's more pages
            if "result_info" in data and data["result_info"]["page"] < data["result_info"]["total_pages"]:
                params["page"] = data["result_info"]["page"] + 1
            else:
                break

        return all_records
    except requests.exceptions.RequestException as e:
        print(f"Error getting zone records: {e}")
        sys.exit(1)

# delete a DNS record
def delete_zone_record(zone_id, api_token, record_id):
    """Delete a specific DNS record."""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()["success"]
    except requests.exceptions.RequestException as e:
        print(f"Error deleting record: {e}")
        sys.exit(1)

# create a new DNS record
def create_zone_record(zone_id, api_token, name, content):
    """Create a new DNS TXT record."""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    record_data = {
        "type": "TXT",
        "name": name,
        "content": content,
        "ttl": 120,  # short TTL
        "proxied": False  # don't proxy TXT records
    }

    try:
        response = requests.post(url, headers=headers, json=record_data)
        response.raise_for_status()
        return response.json()["success"]
    except requests.exceptions.RequestException as e:
        print(f"Error creating record: {e}")
        sys.exit(1)
def letter(file_path, domain, zone_id,api_token, title, author):
    print(f"posting letter: {file_path}")
    if not os.path.isfile(file_path):
        print(f"ERROR 404: File not found!")
        sys.exit(1)
        if not file_path.lower().endswith(".md"):
            print("ERROR file is not a .md (only devs are allowed to post letters)!")
            sys.exit(1)
        with open(file_path, "r") as f:
            data=f.read()
            encoded_letter=encode_data(data)
            chunks=chunk_data(encoded_letter)
            nohash=get_sha256(file_path)
            chunknum=len(chunks)
            print(f"file hash: {nohash}")
            print(f"chunks: {chunknum}")
            print(f"size in bytes: {os.path.getsize(file_path)}")
            