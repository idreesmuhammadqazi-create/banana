#!/usr/bin/env python3
"""
File Download from DNS TXT Records via Direct DNS Queries

This script downloads a file from DNS TXT records stored under a given domain namespace.
It uses direct DNS queries (dnspython) so no API token or zone ID is needed.
It reconstructs the file from the chunks and verifies the SHA-256 hash to ensure integrity.
Works with any file type — because if someone was crazy enough to upload it, we're crazy enough to download it.
"""

import os
import sys
import base64
import hashlib
import argparse
import json
import dns.resolver

# decode base64 data back to binary
def decode_data(encoded_str):
    """Decode URL-safe base64 encoded string back to binary data."""
    # add padding if needed
    padding_needed = 4 - len(encoded_str) % 4
    if padding_needed != 4:
        encoded_str += "=" * padding_needed
    return base64.urlsafe_b64decode(encoded_str.encode("utf-8"))

# query a single TXT record via DNS
def query_txt_record(name):
    """Query a DNS TXT record and return its content string."""
    try:
        answers = dns.resolver.resolve(name, "TXT")
        # combine all strings in the TXT record
        parts = []
        for rdata in answers:
            for txt_string in rdata.strings:
                parts.append(txt_string.decode("utf-8"))
        return "".join(parts)
    except dns.resolver.NXDOMAIN:
        return None
    except dns.resolver.NoAnswer:
        return None
    except Exception as e:
        print(f"ERROR querying {name}: {e}")
        sys.exit(1)

# main download function
def download_png(output_dir, domain):
    """Handle the download process"""
    print("Getting DNS records...")

    # fetch metadata record
    meta_content = query_txt_record(f"meta.{domain}")

    if not meta_content:
        print("ERROR: No metadata found!")
        sys.exit(1)

    try:
        metadata = json.loads(meta_content)
    except json.JSONDecodeError:
        print("ERROR: Bad metadata!")
        sys.exit(1)

    print("Found metadata:")
    print(f"  File: {metadata['filename']}")
    print(f"  Encoding: {metadata['encoding']}")
    print(f"  Total chunks: {metadata['total_chunks']}")
    print(f"  Hash: {metadata['sha256']}")

    # fetch each chunk by index
    total_chunks = metadata["total_chunks"]
    chunk_records = []

    for i in range(total_chunks):
        chunk_name = f"{i:03d}.{domain}"
        content = query_txt_record(chunk_name)

        if content is None:
            print(f"ERROR: Missing chunk {i:03d}!")
            sys.exit(1)

        chunk_records.append((i, content))

        # print progress every 10 chunks
        if (i + 1) % 10 == 0 or (i + 1) == total_chunks:
            print(f"  Fetched chunk {i + 1}/{total_chunks}")

    if len(chunk_records) != total_chunks:
        print(f"ERROR: Expected {total_chunks} chunks, got {len(chunk_records)}")
        sys.exit(1)

    chunk_records.sort(key=lambda x: x[0])
    all_data = "".join([chunk for _, chunk in chunk_records])

    print("Decoding data...")
    try:
        decoded_bytes = decode_data(all_data)
    except Exception as e:
        print(f"ERROR decoding: {e}")
        sys.exit(1)

    print("Checking hash...")
    computed_hash = hashlib.sha256(decoded_bytes).hexdigest()
    if computed_hash != metadata["sha256"]:
        print("ERROR: Hash doesn't match!")
        sys.exit(1)

    output_path = os.path.join(output_dir, metadata["filename"])
    with open(output_path, "wb") as f:
        f.write(decoded_bytes)

    print(f"File saved: {output_path}")
    print(f"Size: {len(decoded_bytes)} bytes")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Download a file from DNS records. Whatever's up there, we'll grab it."
    )

    parser.add_argument("output_dir", help="Where to save the downloaded file")
    parser.add_argument("domain", help="Domain name (e.g. ihostbanana.qzz.io)")

    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)

    download_png(args.output_dir, args.domain)

if __name__ == "__main__":
    main()
