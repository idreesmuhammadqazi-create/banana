import sys
import dns.resolver
import base64
import json
import argparse
import hashlib
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

def decode_data(encoded_str):
    """Decode URL-safe base64 encoded string back to binary data."""
    # add padding if needed
    padding_needed = 4 - len(encoded_str) % 4
    if padding_needed != 4:
        encoded_str += "=" * padding_needed
    return base64.urlsafe_b64decode(encoded_str.encode("utf-8"))
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
def get_letter(domain):
    console = Console()
    subdomain = f"letter.{domain}"
    console.print("[dim]quering dns for metadata...[/dim]")
    meta = query_txt_record(f"meta.{subdomain}")
    if not meta:
        console.print("[red]ERROR: you sure there's a letter up here ? (not everyone is me)[/red]")
        sys.exit(1)
    try:
        metadata = json.loads(meta)
    except json.JSONDecodeError:
        console.print("[red]ERROR: bruh seems like some other guy like me had the same idea(i have no idea what his metadata means)  ![/red]")
        sys.exit(1)
    chunknum = metadata['chunks']
    console.print(f"[dim]fetching {chunknum} chunks...[/dim]")
    allchunks = []
    for i in range(chunknum):
        chunk = f"{i:03d}.{subdomain}"
        chunkval = query_txt_record(chunk)
        if chunkval is None:
            console.print(f"[red]ERROR: empty chunk [/red]")
            sys.exit(1)
        allchunks.append(chunkval)
    encodedblog = "".join(allchunks)
    decodedblog = decode_data(encodedblog)
    if not decodedblog:
        console.print(f"[red]ERROR: failed to decode[/red]")
        sys.exit(1)
    newhash = hashlib.sha256(decodedblog).hexdigest()
    if newhash != metadata['hash']:
        console.print(f"[red]ERROR: hash is not the same (I TOLD YOU NOT TO TAMPER !!!)[/red]")
        sys.exit(1)
    text = decodedblog.decode("utf-8")
    console.print()
    console.print()
    console.print()
    console.print(Panel(
        f"[bold cyan]{metadata['title']}[/bold cyan]\n"
        f"[dim]by[/dim] [bold]{metadata['author']}[/bold]\n"
        f"{metadata['timestamp']}",
        border_style="cyan"
    ))
    console.print()
    console.print(Markdown(text))
def main():
    parser = argparse.ArgumentParser(description="get a blog post from dns")
    parser.add_argument("domain", help="domain storing a blog in dns")
    args = parser.parse_args()
    get_letter(args.domain)
if __name__ == "__main__":
    main()
    