from pathlib import Path
from src import ingest


def test_ingest_main_moves_latest_csv(tmp_path: Path, capsys):
    input_dir = tmp_path / "pre_raw"
    raw_dir = tmp_path / "raw"
    input_dir.mkdir()
    raw_dir.mkdir()

    f1 = input_dir / "old.csv"
    f2 = input_dir / "new.csv"
    f1.write_text("a")
    f2.write_text("b")

    ingest.main(str(input_dir), str(raw_dir))

    # After ingest, latest file should be moved.
    assert not f2.exists()
    assert (raw_dir / "new.csv").exists()

    out = capsys.readouterr().out
    assert "Ingested file is now at:" in out
