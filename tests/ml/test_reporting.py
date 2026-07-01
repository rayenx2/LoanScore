import json
from pathlib import Path

from modelvaultai_ai.reporting import generate_and_save_monitoring_report


def test_monitoring_report_generation_creates_json_and_markdown() -> None:
    reports_dir = Path("reports/test_reporting")
    json_path = reports_dir / "model_monitoring_report.json"
    markdown_path = reports_dir / "model_monitoring_report.md"

    report = generate_and_save_monitoring_report(json_path=json_path, markdown_path=markdown_path)
    saved = json.loads(json_path.read_text(encoding="utf-8"))

    assert json_path.exists()
    assert markdown_path.exists()
    assert report["executive_summary"]
    assert saved["model_health_score"] == report["model_health_score"]
    assert report["top_drifted_features"]
    assert report["recommended_next_steps"]
