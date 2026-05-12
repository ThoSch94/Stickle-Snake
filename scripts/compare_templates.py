#Script to compare all predictor .dat files on test/train XML sets using shape_tester.py


import argparse
import subprocess
from pathlib import Path
import sys

# Run shape_tester.py with the given xml file and predictor, return the exit code
def run_shape_tester(shape_tester_path: Path, xml_file: Path, predictor_file: Path) -> int:
    cmd = [
        sys.executable,
        str(shape_tester_path),
        "-t",
        str(xml_file),
        "-p",
        str(predictor_file),
    ]
    print(f"Processing {xml_file.name.replace('.xml', '')} data: {predictor_file}")
    result = subprocess.run(cmd)
    return result.returncode 

# Compare all predictors in the work_dir against test.xml and train.xml using shape_tester.py. Also checks for failures and reports them at the end.
def compare_predictors(work_dir: Path, shape_tester_path: Path, model_dir: Path, pattern: str = "*.dat") -> int:
    predictors = sorted(model_dir.rglob(pattern))
    if not predictors:
        print(f"No predictors found with pattern: {pattern} in directory: {model_dir}")
        return 1

    datasets = [work_dir / "test.xml", work_dir / "train.xml"]
    for ds in datasets:
        if not ds.exists():
            print(f"Missing required file: {ds}")
            return 1

    overall_failures = 0

    print("Starting test comparison of predictors")
    for pred in predictors:
        rc = run_shape_tester(shape_tester_path, work_dir / "test.xml", pred)
        if rc != 0:
            print(f"Failed on test.xml with predictor {pred} (exit code {rc})")
            overall_failures += 1

    print("..............")
    print("Starting train comparison of predictors")
    for pred in predictors:
        rc = run_shape_tester(shape_tester_path, work_dir / "train.xml", pred)
        if rc != 0:
            print(f"Failed on train.xml with predictor {pred} (exit code {rc})")
            overall_failures += 1

    print("Comparison complete.")
    if overall_failures:
        print(f"Total failed runs: {overall_failures}")
        return 1

    print("All runs completed successfully.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Compare all predictor .dat files on test/train XML sets.")
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path("data/"),
        help="Directory containing predictors and train.xml/test.xml",
    )
    parser.add_argument(
        "--shape-tester",
        type=Path,
        default=Path("scripts/ml-morph_scripts/shape_tester.py"),
        help="Path to shape_tester.py. Defaults to scripts/ml-morph_scripts/shape_tester.py",
    )

    parser.add_argument(
        "--model_dir",
        default=Path("models/"),
        help="Directory containing model files (default: data/models/)",
    )

    parser.add_argument(
        "--pattern",
        default="*.dat",
        help="Glob pattern for predictor files (default: *  .dat)",
    )

    args = parser.parse_args()
    rc = compare_predictors(args.work_dir.resolve(), args.shape_tester.resolve(), args.model_dir.resolve(), args.pattern)
    sys.exit(rc)


if __name__ == "__main__":
    main()