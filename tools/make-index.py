#!/usr/bin/env python3
"""Regenerate index.json (and copy the APK/icon) for this Mihon extension store.

Example:
    python3 tools/make-index.py \
        --source-info path/to/keiyoushi-source-info.json \
        --apk path/to/release.apk \
        --apk-name tachiyomi-all.aq-v1.6.1.apk \
        --icon path/to/icon.png
"""

import argparse
import glob
import json
import os
import shutil
import subprocess

CONTENT_WARNING = {
    0: "CONTENT_WARNING_UNSPECIFIED",
    1: "CONTENT_WARNING_SAFE",
    2: "CONTENT_WARNING_MIXED",
    3: "CONTENT_WARNING_NSFW",
}


def find_apksigner(explicit):
    if explicit:
        return explicit
    android_home = os.environ.get("ANDROID_HOME") or os.path.expanduser("~/android-sdk")
    candidates = sorted(glob.glob(os.path.join(android_home, "build-tools", "*", "apksigner")))
    return candidates[-1] if candidates else "apksigner"


def cert_sha256(apksigner, apk):
    result = subprocess.run(
        [apksigner, "verify", "--print-certs", apk],
        check=True,
        capture_output=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "SHA-256 digest" in line:
            return line.rsplit(":", 1)[-1].strip().replace(":", "").lower()
    raise SystemExit("Could not find certificate SHA-256 digest in apksigner output")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-info", required=True)
    parser.add_argument("--apk", required=True)
    parser.add_argument("--apk-name", help="File name to use inside the store (defaults to the APK's own file name)")
    parser.add_argument("--icon")
    parser.add_argument("--repo", default="AwesomeQuest/my-mihon-ext")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--store-name", default="AwesomeQuest")
    parser.add_argument("--badge", default="AQ")
    parser.add_argument("--apksigner")
    parser.add_argument(
        "--store-dir",
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )
    args = parser.parse_args()

    with open(args.source_info) as f:
        info = json.load(f)

    apk_name = args.apk_name or os.path.basename(args.apk)
    shutil.copyfile(args.apk, os.path.join(args.store_dir, apk_name))

    icon_name = None
    if args.icon:
        icon_name = "icon.png"
        shutil.copyfile(args.icon, os.path.join(args.store_dir, icon_name))

    base = f"https://github.com/{args.repo}/raw/{args.branch}"
    index = {
        "name": args.store_name,
        "badgeLabel": args.badge,
        "signingKey": cert_sha256(find_apksigner(args.apksigner), args.apk),
        "contact": {
            "website": f"https://github.com/{args.repo}",
            "discord": None,
        },
        "extensionList": {
            "extensions": [
                {
                    "name": info["name"],
                    "packageName": info["packageName"],
                    "resources": {
                        "apkUrl": f"{base}/{apk_name}",
                        "iconUrl": f"{base}/{icon_name}" if icon_name else f"{base}/{apk_name}",
                    },
                    "extensionLib": info["extensionLib"],
                    "versionCode": info["versionCode"],
                    "versionName": info["versionName"],
                    "contentWarning": CONTENT_WARNING.get(
                        info["contentWarning"], "CONTENT_WARNING_SAFE"
                    ),
                    "sources": [
                        {
                            "id": source["id"],
                            "name": source["name"],
                            "language": source["lang"],
                            "homeUrl": source["baseUrl"],
                        }
                        for source in info["sources"]
                    ],
                },
            ],
        },
        "extensionListUrl": None,
    }

    out_path = os.path.join(args.store_dir, "index.json")
    with open(out_path, "w") as f:
        json.dump(index, f, indent=2)
        f.write("\n")

    print(f"wrote {out_path}")
    print(f"  apk: {apk_name}")
    print(f"  signingKey: {index['signingKey']}")
    print(f"  version: {info['versionName']} ({info['versionCode']})")


if __name__ == "__main__":
    main()
