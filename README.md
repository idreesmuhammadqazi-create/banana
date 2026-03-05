# Files to DNS TXT Records via Cloudflare API

**Because who doesn't love storing their precious files in DNS records?**

This Python script is your ticket to the wonderful world of abusing DNS for file storage. Because apparently, we haven't tortured the DNS protocol enough already.

## Features

- **Upload Mode**: Takes your innocent file — PNG, JPEG, PDF, ZIP, your grandma's secret recipe in `.docx` — and turns it into a bunch of DNS TXT records. Because why use actual file storage when you can spam DNS servers?
- **Download Mode**: Queries DNS directly like a caveman — no API tokens, no credentials, just raw DNS queries. Because DNS records are public and we're not above exploiting that.
- **Any File Type**: We used to be PNG snobs. Not anymore. If it's a file, we'll shove it into DNS. No questions asked.
- **Open Letters / Blog Posts**: Post Markdown files to DNS and let anyone read them with pretty terminal rendering. It's like Medium, but worse in every conceivable way. 📬
- **Configurable Domain**: All scripts now accept a domain name as a command-line argument. Bring your own domain to the DNS abuse party — we're not picky!
- **Metadata Preservation**: Remembers your filename and other boring details. Because we'd hate for you to forget what you uploaded.
- **Idempotent Upload**: Wipes out old records before creating new ones. Clean slate, every time!
- **Error Handling**: Tries really hard not to break everything. No promises though.

## Requirements

- Python 3.6 or later (we're not supporting dinosaurs here)
- `requests` library for uploading (which you can install with `pip install requests`)
- `dnspython` library for downloading (which you can install with `pip install dnspython`)
- `rich` library for reading letters/blog posts in style (which you can install with `pip install rich`)
- Cloudflare API token (go get one from your Cloudflare dashboard — only needed for **uploading/posting**)
- Cloudflare Zone ID (also available in your Cloudflare dashboard — again, only for **uploading/posting**)

## Setup

1. Install dependencies :
   ```bash
   pip install requests dnspython rich
   ```

2. Get your Cloudflare API token with DNS edit permissions (you'll pass this as a command argument when **uploading** — downloading/reading doesn't need any of that nonsense)

## Usage

### Upload Script

```bash
python upload_png.py <your_file> <domain> <cloudflare_zone_id> <api_token>
```

**Example** :
```bash
python upload_png.py cat_picture.png ihostbanana.qzz.io 0123456789abcdef0123456789abcdef your_api_token_here
```

*Works with any file type now. PNG, JPEG, PDF, ZIP, your tax returns — we don't discriminate. Just don't go too big, or you'll end up with more DNS records than you have friends.*

### Download Script

```bash
python download_png.py <where_to_save> <domain>
```

**Example** (again, because we're nice like that):
```bash
python download_png.py ./my_precious_files ihostbanana.qzz.io
```

*That's it. No API token. No zone ID. Just point it at a directory, tell it which domain to query, and let DNS do its thing. Because DNS records are public, baby — anyone with `dnspython` and a dream can grab your files. Security through obscurity at its finest.*

### Post a Letter / Blog Post 📬

```bash
python letter.py <markdown_file> <domain> <cloudflare_zone_id> <api_token> --title "Your Title" --author "Your Name"
```

**Example** :
```bash
python letter.py letter.md ihostbanana.qzz.io 0123456789abcdef0123456789abcdef your_api_token_here --title "Dear Internet" --author "BananaMan"
```

*Post your hot takes, manifestos, and open letters directly to DNS. It's like blogging, except your hosting provider is the entire global DNS infrastructure. The `--author` flag defaults to "banana guy" because we know our audience.*

### Read a Letter / Blog Post 📖

```bash
python getblog.py <domain>
```

**Example** :
```bash
python getblog.py ihostbanana.qzz.io
```

*That's it. No API token. No credentials. No account. Just a domain name and a dream. The letter gets fetched from DNS, verified for integrity, and rendered as beautiful Markdown right in your terminal using `rich`. It's like RSS but with more DNS abuse.*

### Debug Script

```bash
python debug_records.py <domain> <cloudflare_zone_id>
```

*For when you need to peek behind the curtain and see what DNS records are actually out there. API token is read from the `CF_API_TOKEN` environment variable, because typing secrets into your terminal history is a lifestyle choice we won't judge.*

## How This Madness Works

### Upload Process (The "Breaking Things" Phase)

1. **Reads your file**: Because apparently we trust user input. Any file. Any type. We're not picky.
2. **Computes SHA-256 hash**: To prove we didn't mess with your file. Probably.
3. **Encodes to base64**: Because binary data in DNS is like putting a cat in a blender.
4. **Splits into chunks**: ~200 characters each, because DNS records have limits.
5. **Deletes old records**: just to be sure you dont end up mixing your banana photo with your tax returns
6. **Creates metadata record**: `meta.<domain>` - the big boss record with all the important details (e.g. `meta.ihostbanana.qzz.io`).
7. **Creates chunk records**: `000.<domain>`, `001.<domain>`, etc. - each containing a piece of your data (e.g. `000.ihostbanana.qzz.io`, `001.ihostbanana.qzz.io`).

### Download Process (The "Putting Humpty Dumpty Back Together" Phase)

1. **Queries DNS directly**: Using `dnspython` to fire off raw DNS queries — no Cloudflare API, no credentials, no permission needed. Because DNS is basically a public bulletin board and we're just reading what's pinned up there.
2. **Finds metadata**: Because we need to know what we're dealing with.
3. **Validates chunk count**: To make sure we didn't lose any pieces.
4. **Sorts and concatenates**: Because order matters, even in DNS land.
5. **Decodes back to binary**: computers are weird, but they understand binary.
6. **Verifies SHA-256**: To make sure we didn't break anything... this time.
7. **Saves your file**: In the location you specified, with the original filename and extension. Probably.

### Letter / Blog Post Process (The "DNS is My CMS" Phase)

**Posting** (`letter.py`):
1. **Reads your Markdown**: Only `.md` files allowed — we have standards. Low ones, but still.
2. **Encodes and chunks**: Same base64 + chunking pipeline as file uploads.
3. **Cleans up old letter**: Deletes previous letter records. One letter per domain, take it or leave it.
4. **Creates metadata**: `meta.letter.<domain>` — stores title, author, timestamp, hash, and chunk count.
5. **Creates chunk records**: `000.letter.<domain>`, `001.letter.<domain>`, etc.

**Reading** (`getblog.py`):
1. **Queries DNS**: Fetches metadata from `meta.letter.<domain>`. No credentials needed.
2. **Fetches all chunks**: Grabs each chunk record and stitches them together.
3. **Verifies integrity**: SHA-256 hash check — because we don't trust the internet. Shocking, right?
4. **Renders in terminal**: Uses `rich` to display your Markdown with proper formatting, colors, and a fancy header panel. It's beautiful. We cried.

## Records Structure

All the chaos happens under `*.<domain>` — you pick the domain, we'll trash it (e.g. `*.ihostbanana.qzz.io`):

### File Storage Records
- `meta.<domain>`: The boss record with all the important gossip (filename, encoding, chunk count, SHA-256 hash)
- `000.<domain>`: Chunk #1 - the beginning of your data adventure
- `001.<domain>`: Chunk #2 - the middle bit
- `...`: More chunks than you probably wanted
- `148.<domain>`: The final chunk (or whatever number we end up with)

### Letter / Blog Post Records
- `meta.letter.<domain>`: The letter's metadata (title, author, timestamp, hash, chunk count)
- `000.letter.<domain>`: First chunk of your literary masterpiece
- `001.letter.<domain>`: Second chunk
- `...`: You get the idea

## Important Notes (That You Should Probably Read)

- **TTL**: 120 seconds, because who wants slow DNS updates?
- **Proxying**: Records are NOT proxied. Because that would be too sensible.
- **File Size Limit**: ~10KB recommended. Go bigger and you'll have more DNS records than your ISP can handle.
- **File Types**: Literally anything. PNGs, JPEGs, PDFs, ZIPs, executables, your diary — it's all just bytes to us.
- **Letters**: Must be Markdown (`.md`). We're not savages. Well, we are, but we're savages with formatting standards.
- **Idempotency**: We delete everything before uploading. Clean slate, every single time.
- **Error Messages**: If something breaks, we'll tell you. Probably. With attitude.
- **DNS Propagation**: Might take a few minutes. Patience is a virtue, or so they say.
- **Dependencies**: `requests` is for uploading (Cloudflare API), `dnspython` is for downloading (direct DNS queries), `rich` is for making letters look pretty in your terminal. Install all three like a responsible adult: `pip install requests dnspython rich`

**Disclaimer**: This is probably not the best way to store files or publish blog posts. But hey, it works! Use at your own risk, and don't blame us if your DNS admin hunts you down. 🏃‍♂️
