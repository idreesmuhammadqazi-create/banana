# PNG to DNS TXT Records via Cloudflare API

**Because who doesn't love storing their precious PNG files in DNS records?**

This Python script is your ticket to the wonderful world of abusing DNS for file storage. Because apparently, we haven't tortured the DNS protocol enough already.

## Features

- **Upload Mode**: Takes your innocent PNG file and turns it into a bunch of DNS TXT records. Because why use actual file storage when you can spam DNS servers?
- **Download Mode**: Queries DNS directly like a caveman — no API tokens, no credentials, just raw DNS queries. Because DNS records are public and we're not above exploiting that.
- **Configurable Domain**: All scripts now accept a domain name as a command-line argument. Bring your own domain to the DNS abuse party — we're not picky!
- **Metadata Preservation**: Remembers your filename and other boring details. Because we'd hate for you to forget what you uploaded.
- **Idempotent Upload**: Wipes out old records before creating new ones. Clean slate, every time!
- **Error Handling**: Tries really hard not to break everything. No promises though.

## Requirements

- Python 3.6 or later (we're not supporting dinosaurs here)
- `requests` library for uploading (which you can install with `pip install requests`)
- `dnspython` library for downloading (which you can install with `pip install dnspython`)
- Cloudflare API token (go get one from your Cloudflare dashboard — only needed for **uploading**)
- Cloudflare Zone ID (also available in your Cloudflare dashboard — again, only for **uploading**)

## Setup

1. Install dependencies :
   ```bash
   pip install requests dnspython
   ```

2. Get your Cloudflare API token with DNS edit permissions (you'll pass this as a command argument when **uploading** — downloading doesn't need any of that nonsense)

## Usage

### Upload Script

```bash
python upload_png.py <your_png_file> <domain> <cloudflare_zone_id> <api_token>
```

**Example** :
```bash
python upload_png.py cat_picture.png ihostbanana.qzz.io 0123456789abcdef0123456789abcdef your_api_token_here
```

*Pro tip: Make sure your PNG isn't too big, or you'll end up with more DNS records than you have friends.*

### Download Script

```bash
python download_png.py <where_to_save> <domain>
```

**Example** (again, because we're nice like that):
```bash
python download_png.py ./my_precious_files ihostbanana.qzz.io
```

*That's it. No API token. No zone ID. Just point it at a directory, tell it which domain to query, and let DNS do its thing. Because DNS records are public, baby — anyone with `dnspython` and a dream can grab your files. Security through obscurity at its finest.*

### Debug Script

```bash
python debug_records.py <domain> <cloudflare_zone_id>
```

*For when you need to peek behind the curtain and see what DNS records are actually out there. API token is read from the `CF_API_TOKEN` environment variable, because typing secrets into your terminal history is a lifestyle choice we won't judge.*

## How This Madness Works

### Upload Process (The "Breaking Things" Phase)

1. **Reads your PNG**: Because apparently we trust user input.
2. **Computes SHA-256 hash**: To prove we didn't mess with your file. Probably.
3. **Encodes to base64**: Because binary data in DNS is like putting a cat in a blender.
4. **Splits into chunks**: ~200 characters each, because DNS records have limits.
5. **Deletes old records**: just to be sure you dont end up mixng your banana photo with your cat photo
6. **Creates metadata record**: `meta.<domain>` - the big boss record with all the important details (e.g. `meta.ihostbanana.qzz.io`).
7. **Creates chunk records**: `000.<domain>`, `001.<domain>`, etc. - each containing a piece of your data (e.g. `000.ihostbanana.qzz.io`, `001.ihostbanana.qzz.io`).

### Download Process (The "Putting Humpty Dumpty Back Together" Phase)

1. **Queries DNS directly**: Using `dnspython` to fire off raw DNS queries — no Cloudflare API, no credentials, no permission needed. Because DNS is basically a public bulletin board and we're just reading what's pinned up there.
2. **Finds metadata**: Because we need to know what we're dealing with.
3. **Validates chunk count**: To make sure we didn't lose any pieces.
4. **Sorts and concatenates**: Because order matters, even in DNS land.
5. **Decodes back to binary**: computers are weird, but they understand binary.
6. **Verifies SHA-256**: To make sure we didn't break anything... this time.
7. **Saves your file**: In the location you specified. Probably.

## Records Structure

All the chaos happens under `*.<domain>` — you pick the domain, we'll trash it (e.g. `*.ihostbanana.qzz.io`):
- `meta.<domain>`: The boss record with all the important gossip (filename, encoding, chunk count, SHA-256 hash)
- `000.<domain>`: Chunk #1 - the beginning of your data adventure
- `001.<domain>`: Chunk #2 - the middle bit
- `...`: More chunks than you probably wanted
- `148.<domain>`: The final chunk (or whatever number we end up with)

## Important Notes (That You Should Probably Read)

- **TTL**: 120 seconds, because who wants slow DNS updates?
- **Proxying**: Records are NOT proxied. Because that would be too sensible.
- **File Size Limit**: ~10KB recommended. Go bigger and you'll have more DNS records than your ISP can handle.
- **Idempotency**: We delete everything before uploading. Clean slate, every single time.
- **Error Messages**: If something breaks, we'll tell you. Probably.
- **DNS Propagation**: Might take a few minutes. Patience is a virtue, or so they say.
- **Dependencies**: `requests` is for uploading (Cloudflare API), `dnspython` is for downloading (direct DNS queries). Choose your own adventure, or just install both like a responsible adult.

**Disclaimer**: This is probably not the best way to store files. But hey, it works! Use at your own risk, and don't blame us if your DNS admin hunts you down. 🏃‍♂️
