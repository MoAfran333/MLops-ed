from pathlib import Path

import pandas as pd
from ydata_profiling import ProfileReport


def generate_profile(df: pd.DataFrame, dataset_name: str, output_dir: Path) -> Path:
    """
    Generates a pandas profiling report for the given DataFrame.

    Args:
        df: The pandas DataFrame to profile.
        dataset_name: The name of the dataset (files will be named based on this).
        output_dir: The directory to save the report to.

    Returns:
        Path to the generated HTML report.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{dataset_name}_profile.html"

    # Create the profile report
    # minimal=True used for speed
    profile = ProfileReport(df, title=f"Profiling Report: {dataset_name}", minimal=True)

    # Save to file
    profile.to_file(report_path)
    print(f"Profile report saved to: {report_path}")

    return report_path
