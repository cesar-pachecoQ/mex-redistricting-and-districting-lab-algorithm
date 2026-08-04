from redistricting_lab.cli import main


def test_cli_smoke(capsys) -> None:
    main()
    out = capsys.readouterr().out
    assert "redistricting_lab" in out
