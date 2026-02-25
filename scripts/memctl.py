#!/usr/bin/env python3
"""Small CLI wrapper for Mem API: save, search, and list notes."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

API_BASE = os.getenv("MEM_API_BASE", "https://api.mem.ai")


class MemApiError(RuntimeError):
    """Raised when Mem API returns a non-2xx response."""


def require_api_key() -> str:
    api_key = os.getenv("MEM_API_KEY", "").strip()
    if not api_key:
        raise MemApiError(
            "MEM_API_KEY is not set. Run: export MEM_API_KEY='sk-mem-...'")
    return api_key


def api_request(method: str, path: str, *, body: dict[str, Any] | None = None,
                query: dict[str, Any] | None = None) -> dict[str, Any]:
    api_key = require_api_key()
    url = f"{API_BASE}{path}"

    if query:
        filtered = {k: v for k, v in query.items() if v is not None}
        if filtered:
            url = f"{url}?{urllib.parse.urlencode(filtered)}"

    data: bytes | None = None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, method=method, data=data, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        detail = raw.strip() or exc.reason
        raise MemApiError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise MemApiError(f"Network error: {exc.reason}") from exc


def read_content_arg(content: str | None, file_path: str | None) -> str:
    if content and file_path:
        raise MemApiError("Use either inline content or --file, not both.")
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except OSError as exc:
            raise MemApiError(f"Failed to read file {file_path}: {exc}") from exc
    if content:
        return content.strip()
    raise MemApiError("Missing note content. Provide text or --file <path>.")


def cmd_save(args: argparse.Namespace) -> int:
    content = read_content_arg(args.content, args.file)
    payload: dict[str, Any] = {"content": content}

    if args.collection_id:
        payload["collection_ids"] = args.collection_id
    if args.collection_title:
        payload["collection_titles"] = args.collection_title

    result = api_request("POST", "/v2/notes", body=payload)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print("Saved note")
    print(f"- id: {result.get('id', '')}")
    print(f"- title: {result.get('title', '')}")
    print(f"- updated_at: {result.get('updated_at', '')}")
    return 0


def compact_item(item: dict[str, Any]) -> str:
    note_id = item.get("id", "")
    title = item.get("title", "")
    updated = item.get("updated_at", "")
    snippet = (item.get("snippet") or "").replace("\n", " ").strip()
    return f"- {title}\n  id={note_id} updated={updated}\n  {snippet}"


def cmd_search(args: argparse.Namespace) -> int:
    payload: dict[str, Any] = {"query": args.query, "limit": args.limit}
    if args.collection_id:
        payload["collection_ids"] = args.collection_id
    if args.open_tasks:
        payload["contains_open_tasks"] = True
    if args.tasks:
        payload["contains_tasks"] = True
    if args.images:
        payload["contains_images"] = True
    if args.files:
        payload["contains_files"] = True

    result = api_request("POST", "/v2/notes/search", body=payload)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    results = result.get("results", [])
    if args.limit:
        results = results[:args.limit]
    print(f"Search results: {len(results)}")
    for item in results:
        print(compact_item(item))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    query: dict[str, Any] = {
        "limit": args.limit,
        "order": args.order,
        "cursor": args.cursor,
        "collection_id": args.collection_id,
        "include_content": "true" if args.include_content else None,
    }

    result = api_request("GET", "/v2/notes", query=query)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    notes = result.get("results", [])
    print(f"List notes: {len(notes)}")
    for item in notes:
        print(compact_item(item))

    next_page = result.get("next_page")
    if next_page:
        print("\nNext cursor:")
        print(next_page)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="memctl",
        description="Mem API helper CLI (save/search/list)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    save = sub.add_parser("save", help="Create a note with raw markdown content")
    save.add_argument("content", nargs="?", help="Note content (markdown)")
    save.add_argument("--file", help="Read note content from file")
    save.add_argument("--collection-id", action="append", default=[],
                      help="Collection ID to attach (repeatable)")
    save.add_argument("--collection-title", action="append", default=[],
                      help="Collection title to attach (repeatable)")
    save.add_argument("--json", action="store_true", help="Print raw JSON")
    save.set_defaults(func=cmd_save)

    search = sub.add_parser("search", help="Search notes by query")
    search.add_argument("query", help="Search query")
    search.add_argument("--limit", type=int, default=10, help="Max results")
    search.add_argument("--collection-id", action="append", default=[],
                        help="Filter by collection ID (repeatable)")
    search.add_argument("--open-tasks", action="store_true",
                        help="Only notes with open tasks")
    search.add_argument("--tasks", action="store_true",
                        help="Only notes that contain tasks")
    search.add_argument("--images", action="store_true",
                        help="Only notes that contain images")
    search.add_argument("--files", action="store_true",
                        help="Only notes that contain files")
    search.add_argument("--json", action="store_true", help="Print raw JSON")
    search.set_defaults(func=cmd_search)

    ls = sub.add_parser("list", help="List notes")
    ls.add_argument("--limit", type=int, default=10, help="Max results")
    ls.add_argument("--order", choices=["updated_at", "created_at"],
                    default="updated_at", help="Sort order")
    ls.add_argument("--cursor", help="Pagination cursor")
    ls.add_argument("--collection-id", help="Filter by collection ID")
    ls.add_argument("--include-content", action="store_true",
                    help="Include full markdown content")
    ls.add_argument("--json", action="store_true", help="Print raw JSON")
    ls.set_defaults(func=cmd_list)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except MemApiError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
