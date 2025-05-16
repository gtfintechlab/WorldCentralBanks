#!/usr/bin/env python3
"""
Move Gemini inference CSVs into the main llm_inference_output tree.

Before running, make sure:
  – You’re in the project root (the folder that contains both directories), or
  – Update ROOT to an absolute path.

Usage:
  python move_gemini_outputs.py         # dry-run (shows what would move)
  python move_gemini_outputs.py --commit   # actually moves files
"""
from pathlib import Path
import shutil
import argparse

ROOT = Path(__file__).resolve().parent.parent           # project root
SRC  = ROOT / "configs_gemini_flash"             # source tree
DST  = ROOT / "configs"                    # destination tree

def move_files(commit: bool = False) -> None:
    if not SRC.exists():
        raise FileNotFoundError(f"Source directory {SRC} not found.")

    csv_paths = list(SRC.rglob("*.yaml"))
    print(f"Found {len(csv_paths)} files to move.\n")

    for csv_path in csv_paths:
        rel_path = csv_path.relative_to(SRC)
        parts = rel_path.parts
        
        print(parts)

        if len(parts) < 2:
            # print(f"Skipping malformed path: {rel_path}")
            continue

        bank_name = parts[0]
        file_name = parts[1]  
        print(f"bank_name: {bank_name}, file_name: {file_name}")
        # feature_gemini = parts[1]  # e.g., "certain_gemini"
        filename = parts[-1]       # e.g., "gemini-2.5-pro-preview-03-25_20250418_78516.csv"

        # # Target directory: DST/bank_name/feature_gemini/gemini-2.5-pro-preview-03-25/
        target_dir = DST / bank_name
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / filename
        print(f"target_path: {target_path}")

        if commit:
            shutil.move(str(csv_path), str(target_path))
            print(f"MOVED  {rel_path}  ->  {target_path.relative_to(ROOT)}")
        else:
            print(f"WOULD  {csv_path}  ->  {target_path}")

    if not commit:
        print("\nDry‑run only. Re‑run with --commit to execute.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--commit", action="store_true",
        help="Actually move files (omit for a dry‑run)."
    )
    args = parser.parse_args()
    move_files(args.commit)
