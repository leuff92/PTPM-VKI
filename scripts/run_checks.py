"""Run real unittest suites and retain their output and machine-readable totals."""

import argparse
from datetime import datetime
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import platform
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", action="store_true", help="Test the unchanged lab 1 snapshot")
    args = parser.parse_args()
    if args.baseline:
        spec = importlib.util.spec_from_file_location("triangle", ROOT / "evidence" / "triangle_lab1.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules["triangle"] = module
        spec.loader.exec_module(module)
    reports = ROOT / "results"
    reports.mkdir(exist_ok=True)
    sources = ["evidence/triangle_lab1.py"] if args.baseline else ["triangle.py", "Delivery.py"]
    stats = {
        "tested_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "source_sha256_lf": {
            name: hashlib.sha256((ROOT / name).read_text(encoding="utf-8").encode("utf-8")).hexdigest()
            for name in sources
        },
        "suites": {},
    }
    all_ok = True
    suites = ["triangle"] if args.baseline else ["triangle", "delivery"]
    for name in suites:
        suite = unittest.defaultTestLoader.loadTestsFromName(f"tests.test_{name}")
        output = io.StringIO()
        result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
        suffix = "_baseline" if args.baseline else ""
        (reports / f"{name}{suffix}.txt").write_text(output.getvalue(), encoding="utf-8")
        stats["suites"][name] = {
            "total": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
            "failures": [{"test": test.id(), "traceback": trace} for test, trace in result.failures],
            "errors": [{"test": test.id(), "traceback": trace} for test, trace in result.errors],
            "skipped": len(result.skipped),
        }
        print(f"{name}{suffix}: {result.testsRun} tests, {len(result.failures)} failures, {len(result.errors)} errors")
        all_ok = all_ok and result.wasSuccessful()
    filename = "baseline.json" if args.baseline else "summary.json"
    (reports / filename).write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Nonzero exit code is intentional when the original Delivery.py has defects.
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
