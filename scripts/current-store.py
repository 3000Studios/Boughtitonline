"""Guarded current-store read and scoped theme deployment; never print secrets."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
MUSE = Path(os.environ.get("MUSE_PIPELINE_ROOT", str(Path.home() / "Music" / "3000-Studios-Music-Pipeline")))
sys.path.insert(0, str(MUSE / "scripts"))
from shopify_client import ShopifyClient


def parse_theme_json(value):
    return json.loads(re.sub(r"\A\s*/\*.*?\*/\s*", "", value, flags=re.S))


def digest(value):
    return hashlib.sha256(value.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["status", "deploy"])
    parser.add_argument("--files", nargs="+", default=[])
    args = parser.parse_args()
    manifest = json.loads((ROOT / "docs/current-store-deployment.json").read_text())
    client = ShopifyClient()
    _, domain, version = client._config()
    if domain != manifest["store"]:
        raise RuntimeError("Configured store does not match canonical target")
    shop = client.request("shop.json")["shop"]
    if shop["domain"] != manifest["domain"]:
        raise RuntimeError("Custom domain does not match canonical target")
    themes = client.request("themes.json")["themes"]
    live = [t for t in themes if t["role"] == "main"]
    if len(live) != 1 or live[0]["id"] != manifest["themeId"]:
        raise RuntimeError("Published theme does not match canonical target")
    scopes = {s["handle"] for s in client.access_scopes()["access_scopes"]}
    if not {"read_themes", "write_themes"}.issubset(scopes):
        raise RuntimeError("Required theme scopes are missing")
    print(json.dumps({"status": "CONNECTED", "store": domain, "domain": shop["domain"], "themeId": live[0]["id"]}))
    if args.action == "status":
        return
    files = args.files
    if not files or len(files) != len(set(files)) or not set(files).issubset(manifest["files"]):
        raise RuntimeError("Deployment file list is empty, duplicate, or outside allowlist")
    if git("symbolic-ref", "--short", "HEAD") != "main":
        raise RuntimeError("Deploy only canonical main")
    subprocess.run(["git", "fetch", "origin", "main"], cwd=ROOT, check=True, capture_output=True)
    commit = git("rev-parse", "HEAD")
    if commit != git("rev-parse", "origin/main") or git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("Deploy only clean, pushed source")
    payloads = []
    endpoint = f"themes/{manifest['themeId']}/assets.json"
    for name in files:
        local = git("show", commit + ":" + name)
        parse_theme_json(local)
        remote = client.request(endpoint + "?asset[key]=" + urllib.parse.quote(name, safe=""))["asset"]["value"]
        if parse_theme_json(remote) == parse_theme_json(local):
            print(json.dumps({"file": name, "state": "already matches"}))
            continue
        if digest(remote) != manifest["files"][name]["beforeSha256"]:
            raise RuntimeError("Live file changed since snapshot; refresh before deployment")
        payloads.append((name, local))
    for name, value in payloads:
        remote = client.request(endpoint + "?asset[key]=" + urllib.parse.quote(name, safe=""))["asset"]["value"]
        if parse_theme_json(remote) == parse_theme_json(value):
            continue
        if digest(remote) != manifest["files"][name]["beforeSha256"]:
            raise RuntimeError("Live file changed immediately before write")
        # Call the authenticated sender directly: never replay a failed write.
        client._authenticate()
        request = urllib.request.Request(
            f"https://{domain}/admin/api/{version}/{endpoint}", method="PUT",
            data=json.dumps({"asset": {"key": name, "value": value}}).encode(),
            headers={"X-Shopify-Access-Token": client._token, "Content-Type": "application/json"},
        )
        client._send(request)
        readback = client.request(endpoint + "?asset[key]=" + urllib.parse.quote(name, safe=""))["asset"]["value"]
        # Shopify can normalize JSON whitespace; compare parsed structure.
        if parse_theme_json(readback) != parse_theme_json(value):
            raise RuntimeError("Deployment readback did not match")
        print(json.dumps({"file": name, "state": "deployed and verified", "commit": commit}))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Provider errors may contain sensitive URLs or payloads. Emit only type.
        message = str(error) if type(error) is RuntimeError else type(error).__name__
        print("Current-store operation failed safely: " + message, file=sys.stderr)
        sys.exit(1)
