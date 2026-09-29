"""Run every builder in order.  Usage: /root/bench/hle-venv/bin/python scripts/build_all.py [--out-dir DIR]"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_boundary  # noqa: E402
import build_capability  # noqa: E402
import build_classification  # noqa: E402
import build_execution_mode  # noqa: E402
import build_splits  # noqa: E402

if __name__ == "__main__":
    argv = sys.argv[1:]
    for mod in (build_classification, build_boundary, build_execution_mode, build_capability, build_splits):
        mod.main(argv)
