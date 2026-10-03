from hyperstratum import cli

from conftest import PINS, write


def run(root, *extra):
    return cli.main(["check", "--root", str(root), "--no-git", *extra], pins=PINS,
                    blob_lookup=lambda s, p: None)


def test_clean_fixture_passes_with_info_only(root, capsys):
    assert run(root) == 0
    assert "PENDING_PIN" in capsys.readouterr().out


def test_missing_ref_fails(root, capsys):
    write(root / "wiki/bad.md", "[[beta:gone.md]]\n")
    assert run(root) == 1
    assert "MISSING_FILE" in capsys.readouterr().out


def test_strict_turns_warnings_into_failures(root):
    (root / "fields/beta/docs/one.md").write_text("# One\nL2\n" "[stale](https://github.com/TimeLordRaps/beta/blob/" + "e" * 40 + "/x.md)\n")
    write(root / "fields/alpha/stale.md", "[s](https://github.com/TimeLordRaps/beta/blob/" + "e" * 40 + "/x.md)\n")
    assert run(root) == 0
    assert run(root, "--strict") == 1


def test_build_command_writes_site_and_lock(root, tmp_path):
    out = tmp_path / "o"
    code = cli.main(["build", "--root", str(root), "--out", str(out), "--no-git"], pins=PINS,
                    blob_lookup=lambda s, p: None)
    assert code == 0 and (out / "index.html").is_file()
    code = cli.main(["lock", "--root", str(root), "--no-git"], pins=PINS, blob_lookup=lambda s, p: None)
    assert code == 0 and (root / "wiki.lock.json").is_file()
