#!/usr/bin/env python3
"""
Compare provenance lineage graph JSON before and after CustomGraph parsing.

Helps decide:
  A) API / Neo4j layer returns no edges (no ``links`` / ``edges`` in JSON, or empty arrays).
  B) Client drops edges: raw ``LineageResponse.graph`` has edge data under a key
     ``CustomGraph`` does not map (only ``links`` and ``edges`` are wired today).
  C) Edge rows fail ``GraphProperty`` validation (script will show if CustomGraph
     construction raises).

Live call (same env vars as integration tests: DOMAIN, REALM_NAME,
PROVENA_ADMIN_OFFLINE_TOKEN, CLIENT_ID; optional .env via python-dotenv):

  poetry run python scripts/diagnose_lineage_graph.py 10378.1/1234567 --depth 1

Post-mortem from a saved HTTP JSON body (full LineageResponse object):

  poetry run python scripts/diagnose_lineage_graph.py --json-file /path/to/body.json

Install deps from repo root (``poetry install``).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from ProvenaInterfaces.ProvenanceAPI import LineageResponse

# Repo root on sys.path when run as ``python scripts/diagnose_lineage_graph.py``
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _summarise_graph_blob(blob: Mapping[str, Any] | None) -> dict[str, Any]:
    if blob is None:
        return {"present": False}
    keys = sorted(blob.keys())
    out: dict[str, Any] = {"present": True, "top_level_keys": keys}
    for k in ("links", "edges", "nodes", "directed", "multigraph"):
        if k not in blob:
            continue
        v = blob[k]
        if isinstance(v, list):
            out[f"{k}_len"] = len(v)
            if v and isinstance(v[0], dict):
                out[f"{k}_first_item_keys"] = sorted(v[0].keys())
        else:
            out[k] = repr(v)[:200]
    unknown = [k for k in keys if k not in {"links", "edges", "nodes", "directed", "multigraph", "graph"}]
    out["other_keys"] = unknown
    return out


def _print_section(title: str, body: str) -> None:
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}\n{body.rstrip()}\n")


async def _live(starting_id: str, depth: int) -> None:
    from dotenv import load_dotenv

    from provenaclient.auth import OfflineFlow
    from provenaclient.modules.provena_client import ProvenaClient
    from provenaclient.utils.config import Config
    from ProvenaInterfaces.ProvenanceAPI import LineageResponse

    load_dotenv(_ROOT / ".env")
    domain = os.getenv("DOMAIN")
    realm_name = os.getenv("REALM_NAME")
    offline_token = os.getenv("PROVENA_ADMIN_OFFLINE_TOKEN")
    client_id = os.getenv("CLIENT_ID")
    
    
    missing = [n for n, v in [
        ("DOMAIN", domain),
        ("REALM_NAME", realm_name),
        ("PROVENA_ADMIN_OFFLINE_TOKEN", offline_token),
        ("CLIENT_ID", client_id),
    ] if not v]
    if missing:
        print("Missing env:", ", ".join(missing), file=sys.stderr)
        sys.exit(1)
    assert domain and realm_name and offline_token and client_id  # for type checker

    auth = OfflineFlow(
        config=Config(domain=domain, realm_name=realm_name),
        client_id=client_id,
        offline_token=offline_token,
        offline_token_file=None,
    )
    # Match integration tests: API host for ProvenaClient is fixed in tests.
    client = ProvenaClient(
        config=Config(domain="dev.rrap-is.com", realm_name="rrap"),
        auth=auth,
    )

    raw = await client._prov_client.explore_upstream(starting_id=starting_id, depth=depth)
    assert isinstance(raw, LineageResponse)
    _analyse(raw)


def _from_json(path: Path) -> None:
    from ProvenaInterfaces.ProvenanceAPI import LineageResponse

    data = json.loads(path.read_text(encoding="utf-8"))
    raw = LineageResponse.model_validate(data)
    _analyse(raw)


def _analyse(raw: "LineageResponse") -> None:
    from pydantic import ValidationError

    from provenaclient.models.general import CustomLineageResponse

    blob = raw.graph if isinstance(raw.graph, dict) else None
    _print_section("1) LineageResponse.graph (L2 / untyped dict)", json.dumps(_summarise_graph_blob(blob), indent=2))
    if isinstance(blob, dict) and blob:
        sample = {k: blob[k] for k in list(blob)[:12]}
        _print_section(
            "2) Raw graph blob (truncated values)",
            json.dumps(sample, indent=2, default=str)[:16000],
        )

    dump = raw.model_dump(mode="python")
    _print_section("3) LineageResponse.model_dump() graph keys", json.dumps(sorted((dump.get("graph") or {}).keys()), indent=2))

    try:
        typed = CustomLineageResponse.model_validate(dump)
    except ValidationError as e:
        _print_section("4) CustomLineageResponse.model_validate FAILED", str(e))
        return

    g = typed.graph
    _print_section(
        "5) After CustomGraph parse",
        json.dumps(
            {
                "nodes_len": len(g.nodes) if g else None,
                "links_len": len(g.links) if g else None,
                "first_link": (g.links[0].model_dump() if g and g.links else None),
            },
            indent=2,
        ),
    )

    diag: list[str] = []
    if not isinstance(blob, dict):
        diag.append("graph is not a dict — unexpected shape from API.")
    else:
        lk, ek = blob.get("links"), blob.get("edges")
        if isinstance(lk, list) and len(lk) > 0 and typed.graph and len(typed.graph.links) == 0:
            diag.append(
                "Raw has non-empty ``links`` but CustomGraph.links is empty — "
                "link objects may not match GraphProperty (type/source/target)."
            )
        if isinstance(ek, list) and len(ek) > 0 and typed.graph and len(typed.graph.links) == 0:
            diag.append(
                "Raw has ``edges`` but links stayed empty — check ``edges`` item shape "
                "or extend CustomGraph aliases."
            )
        if (not lk or (isinstance(lk, list) and len(lk) == 0)) and (
            not ek or (isinstance(ek, list) and len(ek) == 0)
        ):
            diag.append(
                "No ``links`` or ``edges`` arrays (or both empty) in API JSON — "
                "likely upstream graph / Neo4j query or serialization, not client-only."
            )
    _print_section("6) Interpretation", "\n".join(diag) if diag else "(No automatic conclusion — inspect sections above.)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("starting_id", nargs="?", help="Registry handle to pass as starting_id")
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--json-file", type=Path, help="Analyse saved LineageResponse JSON from disk")
    args = parser.parse_args()

    if args.json_file:
        _from_json(args.json_file)
        return
    if not args.starting_id:
        parser.error("starting_id is required unless --json-file is set")
    asyncio.run(_live(args.starting_id, args.depth))


if __name__ == "__main__":
    main()
