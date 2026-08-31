#!/usr/bin/env python3
"""Verify that every Mach-O file in an app bundle supports one architecture."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


CPU_NAMES = {
    0x00000007: "x86",
    0x01000007: "x86_64",
    0x0000000C: "arm",
    0x0100000C: "arm64",
}

THIN_MAGICS = {
    b"\xce\xfa\xed\xfe": "<",
    b"\xcf\xfa\xed\xfe": "<",
    b"\xfe\xed\xfa\xce": ">",
    b"\xfe\xed\xfa\xcf": ">",
}

FAT_MAGICS = {
    b"\xca\xfe\xba\xbe": (">", 20),
    b"\xbe\xba\xfe\xca": ("<", 20),
    b"\xca\xfe\xba\xbf": (">", 32),
    b"\xbf\xba\xfe\xca": ("<", 32),
}


def macho_architectures(path: Path) -> set[str]:
    with path.open("rb") as file:
        header = file.read(8)
        if len(header) < 8:
            return set()

        endian = THIN_MAGICS.get(header[:4])
        if endian is not None:
            cpu_type = struct.unpack(f"{endian}I", header[4:8])[0]
            return {CPU_NAMES.get(cpu_type, f"cpu-0x{cpu_type:08x}")}

        fat_format = FAT_MAGICS.get(header[:4])
        if fat_format is None:
            return set()
        endian, entry_size = fat_format
        architecture_count = struct.unpack(f"{endian}I", header[4:8])[0]
        if architecture_count > 256:
            raise ValueError(f"Invalid Mach-O architecture count in {path}")

        architectures = set()
        for _ in range(architecture_count):
            entry = file.read(entry_size)
            if len(entry) != entry_size:
                raise ValueError(f"Truncated Mach-O architecture table in {path}")
            cpu_type = struct.unpack(f"{endian}I", entry[:4])[0]
            architectures.add(CPU_NAMES.get(cpu_type, f"cpu-0x{cpu_type:08x}"))
        return architectures


def verify_bundle(app_path: Path, expected_arch: str) -> int:
    app_path = Path(app_path)
    if not app_path.is_dir():
        raise ValueError(f"App bundle not found: {app_path}")

    checked = 0
    mismatches: list[str] = []
    for path in sorted(item for item in app_path.rglob("*") if item.is_file()):
        architectures = macho_architectures(path)
        if not architectures:
            continue
        checked += 1
        if expected_arch not in architectures:
            found = ", ".join(sorted(architectures))
            mismatches.append(f"{path}: expected {expected_arch}, found {found}")

    if checked == 0:
        raise ValueError(f"No Mach-O files found in {app_path}")
    if mismatches:
        raise ValueError("Architecture mismatch:\n" + "\n".join(mismatches))
    return checked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--expected-arch", choices=("arm64", "x86_64"), required=True)
    args = parser.parse_args()

    checked = verify_bundle(args.app, args.expected_arch)
    print(f"Verified {checked} Mach-O files for {args.expected_arch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
