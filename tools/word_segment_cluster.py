"""K-means clustering of extracted word segments + interactive labeler.

Clusters segments by acoustic features (FFT signature + duration).
Same words tend to cluster together. Then provides interactive CLI
to listen to cluster representatives and assign labels.

Usage:
  python tools/word_segment_cluster.py cluster <segments_dir> --k 30
  python tools/word_segment_cluster.py label <segments_dir> --cluster_id 5
  python tools/word_segment_cluster.py extract <segments_dir> --label and --out_dir <where>
"""
from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
from pathlib import Path

import numpy as np


def cmd_cluster(args):
    """K-means cluster all segments by FFT signature + duration."""
    index_path = args.segments_dir / "index.json"
    index = json.loads(index_path.read_text())
    segments = index["segments"]
    n = len(segments)
    if n == 0:
        print("No segments found", file=sys.stderr)
        return

    sigs = np.array([s["fft_signature"] for s in segments])
    durs = np.array([[s["duration_seconds"]] for s in segments])
    # standardize duration so it's same scale as fft sig (0..1)
    dur_norm = (durs - durs.min()) / max(durs.max() - durs.min(), 1e-6)
    features = np.concatenate([sigs, dur_norm], axis=1)

    rng = np.random.default_rng(42)
    init_idx = rng.choice(n, size=args.k, replace=False)
    centroids = features[init_idx].copy()
    assignments = np.zeros(n, dtype=int)

    for it in range(50):
        # assign
        dists = np.linalg.norm(features[:, None, :] - centroids[None, :, :], axis=2)
        new_assignments = dists.argmin(axis=1)
        if np.all(new_assignments == assignments) and it > 0:
            break
        assignments = new_assignments
        # update
        for c in range(args.k):
            members = features[assignments == c]
            if len(members) > 0:
                centroids[c] = members.mean(axis=0)

    # Write cluster info back into index
    cluster_sizes = np.bincount(assignments, minlength=args.k)
    for i, seg in enumerate(segments):
        seg["cluster_id"] = int(assignments[i])
    index["k_clusters"] = args.k
    index["cluster_sizes"] = cluster_sizes.tolist()
    index_path.write_text(json.dumps(index, indent=2))

    print(f"Clustered {n} segments into {args.k} groups", file=sys.stderr)
    print("Cluster sizes (sorted by size, top 15):", file=sys.stderr)
    sorted_clusters = sorted(enumerate(cluster_sizes), key=lambda kv: -kv[1])
    for cid, size in sorted_clusters[:15]:
        # avg duration in cluster
        members = [s for s in segments if s["cluster_id"] == cid]
        avg_dur = np.mean([s["duration_seconds"] for s in members])
        print(f"  cluster {cid:3d}: {size:4d} segments, avg duration {avg_dur*1000:.0f}ms",
              file=sys.stderr)


def _afplay(path):
    """Play a WAV via macOS afplay."""
    try:
        subprocess.run(["afplay", str(path)], timeout=5, check=False,
                       stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"  afplay error: {e}", file=sys.stderr)


def cmd_label(args):
    """Interactive label assignment for a specific cluster."""
    index_path = args.segments_dir / "index.json"
    index = json.loads(index_path.read_text())
    segments = index["segments"]
    members = [s for s in segments if s.get("cluster_id") == args.cluster_id]
    if not members:
        print(f"No segments in cluster {args.cluster_id}", file=sys.stderr)
        return

    print(f"\nCluster {args.cluster_id}: {len(members)} segments", file=sys.stderr)
    print(f"  avg duration {np.mean([s['duration_seconds'] for s in members])*1000:.0f}ms",
          file=sys.stderr)
    print(f"\nWill play up to {args.sample_n} samples. After each, type label or skip.\n"
          f"Common labels: and, the, of, to, a, in, that, it, is, was\n"
          f"Type 'r' to replay, '' to skip, label name to set, 'q' to quit\n"
          f"Type 'all <label>' to assign label to ALL segments in this cluster\n",
          file=sys.stderr)

    random.seed(42)
    sample = random.sample(members, min(args.sample_n, len(members)))
    for i, seg in enumerate(sample):
        while True:
            print(f"\n[{i+1}/{len(sample)}] dur {seg['duration_seconds']*1000:.0f}ms "
                  f"path={Path(seg['segment_path']).name}", file=sys.stderr)
            _afplay(seg["segment_path"])
            label = input("label> ").strip().lower()
            if label == "":
                break
            if label == "q":
                # save and quit
                index_path.write_text(json.dumps(index, indent=2))
                return
            if label == "r":
                continue
            if label.startswith("all "):
                bulk_label = label[4:].strip()
                for s in members:
                    s["label"] = bulk_label
                print(f"  Assigned label '{bulk_label}' to all {len(members)} cluster members",
                      file=sys.stderr)
                index_path.write_text(json.dumps(index, indent=2))
                return
            # set label for this single sample
            for s in segments:
                if s["segment_path"] == seg["segment_path"]:
                    s["label"] = label
                    break
            index_path.write_text(json.dumps(index, indent=2))
            break

    index_path.write_text(json.dumps(index, indent=2))
    print(f"\nDone with cluster {args.cluster_id}", file=sys.stderr)


def cmd_extract(args):
    """Extract all segments with a given label."""
    index_path = args.segments_dir / "index.json"
    index = json.loads(index_path.read_text())
    matching = [s for s in index["segments"] if s.get("label") == args.label]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_index = {
        "label": args.label,
        "n": len(matching),
        "segments": matching,
    }
    (args.out_dir / f"{args.label}_index.json").write_text(json.dumps(out_index, indent=2))
    print(f"Found {len(matching)} segments labeled '{args.label}'", file=sys.stderr)
    print(f"Wrote index to {args.out_dir / f'{args.label}_index.json'}", file=sys.stderr)


def cmd_summary(args):
    """Show label summary."""
    index_path = args.segments_dir / "index.json"
    index = json.loads(index_path.read_text())
    segments = index["segments"]
    labels = {}
    for s in segments:
        l = s.get("label") or "(unlabeled)"
        labels[l] = labels.get(l, 0) + 1
    print(f"\nTotal segments: {len(segments)}")
    print(f"Total clusters: {index.get('k_clusters', '?')}")
    print(f"\nLabels:")
    for l, count in sorted(labels.items(), key=lambda kv: -kv[1]):
        print(f"  {l:20s}: {count}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    c1 = sub.add_parser("cluster")
    c1.add_argument("segments_dir", type=Path)
    c1.add_argument("--k", type=int, default=30)

    c2 = sub.add_parser("label")
    c2.add_argument("segments_dir", type=Path)
    c2.add_argument("--cluster_id", type=int, required=True)
    c2.add_argument("--sample_n", type=int, default=8)

    c3 = sub.add_parser("extract")
    c3.add_argument("segments_dir", type=Path)
    c3.add_argument("--label", required=True)
    c3.add_argument("--out_dir", type=Path, required=True)

    c4 = sub.add_parser("summary")
    c4.add_argument("segments_dir", type=Path)

    args = ap.parse_args()
    if args.cmd == "cluster":
        cmd_cluster(args)
    elif args.cmd == "label":
        cmd_label(args)
    elif args.cmd == "extract":
        cmd_extract(args)
    elif args.cmd == "summary":
        cmd_summary(args)


if __name__ == "__main__":
    main()
