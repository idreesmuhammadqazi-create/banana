#!/usr/bin/env python3
"""
PNG Download from DNS TXT Records via Cloudflare API

This script downloads a PNG file from DNS TXT records stored under the *.ihostbanana.qzz.io namespace.
It reconstructs the file from the chunks and verifies the SHA-256 hash to ensure integrity.
"""

import os
import sys
import base64
import hashlib
import argparse
import requests
import json

# decode base64 data back to binary
def decode_data(encoded_str):
    """Decode URL-safe base64 encoded string back to binary data."""
    # add padding if needed
    padding_needed = 4 - len(encoded_str) % 4
    if padding_needed != 4:
        encoded_str += "=" * padding_needed
    return base64.urlsafe_b64decode(encoded_str.encode("utf-8"))

# get all the DNS records we care about
def get_zone_records(zone_id, api_token, domain_pattern="ihostbanana.qzz.io"):
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

# main download function
def download_png(output_dir, zone_id, api_token):
    """Handle the download process"""
    print("Getting DNS records...")

    # get all records
    records = get_zone_records(zone_id, api_token)

    if not records:
        print("ERROR: No records found!")
        sys.exit(1)

    # find the metadata record
    metadata = None
    chunk_records = []

    for record in records:
        # cloudflare puts quotes around TXT content
        content = record["content"].strip('"')

        if record["name"] == "meta.ihostbanana.qzz.io":
            try:
                metadata = json.loads(content)
            except json.JSONDecodeError:
                print("ERROR: Bad metadata!")
                sys.exit(1)
        elif record["name"].endswith(".ihostbanana.qzz.io") and record["name"] != "meta.ihostbanana.qzz.io":
            # get the chunk number from the subdomain
            try:
                index = int(record["name"].split(".")[0])
                chunk_records.append((index, content))
            except ValueError:
                continue

    if not metadata:
        print("ERROR: No metadata found!")
        sys.exit(1)

    print("Found metadata:")
    print(f"  File: {metadata['filename']}")
    print(f"  Encoding: {metadata['encoding']}")
    print(f"  Total chunks: {metadata['total_chunks']}")
    print(f"  Hash: {metadata['sha256']}")

    # check we have all chunks
    if len(chunk_records) != metadata["total_chunks"]:
        print(f"ERROR: Expected {metadata['total_chunks']} chunks, got {len(chunk_records)}")
        sys.exit(1)

    # sort chunks and put them together
    chunk_records.sort(key=lambda x: x[0])
    all_data = "".join([chunk for _, chunk in chunk_records])

    # decode the data
    print("Decoding data...")
    try:
        decoded_bytes = decode_data(all_data)
    except Exception as e:
        print(f"ERROR decoding: {e}")
        sys.exit(1)

    # check the hash
    print("Checking hash...")
    computed_hash = hashlib.sha256(decoded_bytes).hexdigest()
    if computed_hash != metadata["sha256"]:
        print("ERROR: Hash doesn't match!")
        sys.exit(1)

    # save the file
    output_path = os.path.join(output_dir, metadata["filename"])
    with open(output_path, "wb") as f:
        f.write(decoded_bytes)

    print(f"File saved: {output_path}")
    print(f"Size: {len(decoded_bytes)} bytes")

# main function for command line
def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Download PNG from DNS records"
    )

    parser.add_argument("output_dir", help="Where to save the PNG")
    parser.add_argument("zone_id", help="Cloudflare Zone ID")
    parser.add_argument("api_token", help="API token")

    args = parser.parse_args()

    # make sure output dir exists
    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)

    download_png(args.output_dir, args.zone_id, args.api_token)

# run the program
if __name__ == "__main__":
    main()
