# PNG to DNS TXT Records via Cloudflare API

**Because who doesn't love storing their precious PNG files in DNS records?** 

This Python script is your ticket to the wonderful world of abusing DNS for file storage. Because apparently, we haven't tortured the DNS protocol enough already.

## Features

- **Upload Mode**: Takes your innocent PNG file and turns it into a bunch of DNS TXT records. Because why use actual file storage when you can spam DNS servers?
- **Download Mode**: Magically reassembles your PNG from DNS records. Hopefully without any corruption... hopefully.
- **Metadata Preservation**: Remembers your filename and other boring details. Because we'd hate for you to forget what you uploaded.
- **Idempotent Upload**: Wipes out old records before creating new ones. Clean slate, every time!
- **Error Handling**: Tries really hard not to break everything. No promises though.

## Requirements

- Python 3.6 or later (we're not supporting dinosaurs here)
- `requests` library (which you can install with `pip install requests`)
- Cloudflare API token (go get one from your Cloudflare dashboard)
- Cloudflare Zone ID (also available in your Cloudflare dashboard)

## Setup

1. Install dependencies :
   ```bash
   pip install requests
   ```

2. Get your Cloudflare API token with DNS edit permissions (you'll pass this as a command argument)

## Usage

### Upload Script

```bash
python upload_png.py <your_png_file> <cloudflare_zone_id> <api_token>
```

**Example** :
```bash
python upload_png.py cat_picture.png 0123456789abcdef0123456789abcdef your_api_token_here
```

*Pro tip: Make sure your PNG isn't too big, or you'll end up with more DNS records than you have friends.*

### Download Script

```bash
python download_png.py <where_to_save> <cloudflare_zone_id> <api_token>
```

**Example** (again, because we're nice like that):
```bash
python download_png.py ./my_precious_files 0123456789abcdef0123456789abcdef your_api_token_here
```

## How This Madness Works

### Upload Process (The "Breaking Things" Phase)

1. **Reads your PNG**: Because apparently we trust user input.
2. **Computes SHA-256 hash**: To prove we didn't mess with your file. Probably.
3. **Encodes to base64**: Because binary data in DNS is like putting a cat in a blender.
4. **Splits into chunks**: ~200 characters each, because DNS records have limits.
5. **Deletes old records**: just to be sure you dont end up mixng your banana photo with your cat photo
6. **Creates metadata record**: `meta.ihostbanana.qzz.io` - the big boss record with all the important details.
7. **Creates chunk records**: `000.ihostbanana.qzz.io`, `001.ihostbanana.qzz.io`, etc. - each containing a piece of your data.

### Download Process (The "Putting Humpty Dumpty Back Together" Phase)

1. **Fetches all records**: From the magical `*.ihostbanana.qzz.io` namespace.
2. **Finds metadata**: Because we need to know what we're dealing with.
3. **Validates chunk count**: To make sure we didn't lose any pieces.
4. **Sorts and concatenates**: Because order matters, even in DNS land.
5. **Decodes back to binary**: computers are weird, but they understand binary.
6. **Verifies SHA-256**: To make sure we didn't break anything... this time.
7. **Saves your file**: In the location you specified. Probably.

## Records Structure

All the chaos happens under `*.ihostbanana.qzz.io` (because why not?):
- `meta.ihostbanana.qzz.io`: The boss record with all the important gossip (filename, encoding, chunk count, SHA-256 hash)
- `000.ihostbanana.qzz.io`: Chunk #1 - the beginning of your data adventure
- `001.ihostbanana.qzz.io`: Chunk #2 - the middle bit
- `...`: More chunks than you probably wanted
- `148.ihostbanana.qzz.io`: The final chunk (or whatever number we end up with)

## Important Notes (That You Should Probably Read)

- **TTL**: 120 seconds, because who wants slow DNS updates?
- **Proxying**: Records are NOT proxied. Because that would be too sensible.
- **File Size Limit**: ~10KB recommended. Go bigger and you'll have more DNS records than your ISP can handle.
- **Idempotency**: We delete everything before uploading. Clean slate, every single time.
- **Error Messages**: If something breaks, we'll tell you. Probably.
- **DNS Propagation**: Might take a few minutes. Patience is a virtue, or so they say.
- **Cost**: Cloudflare might charge you for all these DNS queries. You're welcome.

**Disclaimer**: This is probably not the best way to store files. But hey, it works! Use at your own risk, and don't blame us if your DNS admin hunts you down. 🏃‍♂️