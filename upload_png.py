#!/usr/bin/env python3
"""
PNG Upload to DNS TXT Records via Cloudflare API
This script uploads a PNG file by encoding it into base64 and splitting it into
chunks stored in DNS TXT records. It also creates a metadata record for reconstruction.
"""

import os
import sys
import base64
import hashlib
import argparse
import requests
import json

# this function gets the hash of a file
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

# main upload function
def upload_png(file_path, domain, zone_id, api_token):
    """Handle the upload process"""
    print(f"Uploading file: {file_path}")

    # check if file exists
    if not os.path.isfile(file_path):
        print(f"ERROR: File {file_path} not found!")
        sys.exit(1)

    # check if it's a PNG
    if not file_path.lower().endswith(".png"):
        print("ERROR: Must be a PNG file!")
        sys.exit(1)

    # read the file
    with open(file_path, "rb") as f:
        file_data = f.read()

    # encode it
    encoded_stuff = encode_data(file_data)
    chunks = chunk_data(encoded_stuff)
    file_name = os.path.basename(file_path)
    file_hash = get_sha256(file_path)
    num_chunks = len(chunks)

    print(f"File size: {len(file_data)} bytes")
    print(f"Encoded: {len(encoded_stuff)} chars")
    print(f"Chunks needed: {num_chunks}")
    print(f"Hash: {file_hash}")

    # delete old records first
    print("Cleaning up old records...")
    old_records = get_zone_records(zone_id, api_token, domain)
    for record in old_records:
        delete_zone_record(zone_id, api_token, record["id"])
        print(f"Deleted: {record['name']}")

    # make metadata record
    meta_info = {
        "filename": file_name,
        "encoding": "base64url",
        "total_chunks": num_chunks,
        "sha256": file_hash
    }
    meta_json = json.dumps(meta_info)
    success = create_zone_record(zone_id, api_token, f"meta.{domain}", meta_json)
    if success:
        print("Made metadata record")
    else:
        print("Failed to make metadata!")
        sys.exit(1)

    # make all the chunk records
    print("Making chunk records...")
    for i, chunk in enumerate(chunks):
        record_name = f"{i:03d}.{domain}"
        create_zone_record(zone_id, api_token, record_name, chunk)
        if (i + 1) % 10 == 0 or i + 1 == num_chunks:
            print(f"Done {i + 1}/{num_chunks} chunks")

    print("Upload finished!")

# main function for command line
def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Upload PNG to DNS records"
    )

    parser.add_argument("file_path", help="PNG file to upload")
    parser.add_argument("domain", help="Domain name (e.g. ihostbanana.qzz.io)")
    parser.add_argument("zone_id", help="Cloudflare Zone ID")
    parser.add_argument("api_token", help="API token")

    args = parser.parse_args()

    upload_png(args.file_path, args.domain, args.zone_id, args.api_token)

# run the program
if __name__ == "__main__":
    main()