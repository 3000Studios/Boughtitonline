"""Validate product template references, including the installed hosted widget."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_BLOCK = "shopify://apps/judge-me-reviews/blocks/review_widget/61ccd3b1-a9f2-4160-9fe9-4fec8413e5d8"


def check_reference(block_type, directory):
    if directory == "blocks" and block_type == APP_BLOCK:
        return
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", block_type):
        raise ValueError(f"Unapproved {directory} reference: {block_type}")
    if not (ROOT / directory / f"{block_type}.liquid").is_file():
        raise ValueError(f"Missing {directory} reference: {block_type}")


def check_blocks(blocks):
    for block in blocks.values():
        check_reference(block["type"], "blocks")
        check_blocks(block.get("blocks", {}))


def main():
    template = json.loads((ROOT / "templates/product.json").read_text(encoding="utf-8"))
    for section in template["sections"].values():
        check_reference(section["type"], "sections")
        check_blocks(section.get("blocks", {}))
    print("Product template section, theme block and hosted app references passed")


if __name__ == "__main__":
    main()
