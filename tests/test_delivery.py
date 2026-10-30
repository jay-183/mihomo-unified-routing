import hashlib
import contextlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.build import build
from scripts.model import ROOT
from scripts.model import load_model
from scripts.publish import git, publish
from scripts.sync_verge import install_script


class SafeDelivery(unittest.TestCase):
    def test_failed_refresh_keeps_previous_dist(self):
        previous = (ROOT / "dist/manifest.json").read_bytes()
        with patch("scripts.build.fetch_provider", side_effect=RuntimeError("download failed")):
            with self.assertRaises(RuntimeError):
                build("https://example.com/release", refresh=True)
        self.assertEqual(previous, (ROOT / "dist/manifest.json").read_bytes())

    def test_failed_staged_validation_keeps_previous_dist(self):
        previous = (ROOT / "dist/manifest.json").read_bytes()
        with patch("scripts.validate.validate_dist", side_effect=ValueError("invalid staged configuration")):
            with self.assertRaises(ValueError):
                build("https://example.com/release")
        self.assertEqual(previous, (ROOT / "dist/manifest.json").read_bytes())

    def test_failed_swap_preserves_backup_even_when_restore_also_fails(self):
        for restore_fails in (False, True):
            with self.subTest(restore_fails=restore_fails), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                (root / "dist").mkdir()
                (root / "dist/marker").write_text("previous working output")
                rename = Path.rename

                def fail_swap(path, destination):
                    if path.name == "dist" and path.parent.name.startswith("build-"):
                        raise OSError("replacement failed")
                    if path.name == "dist-previous" and restore_fails:
                        raise OSError("restore failed")
                    return rename(path, destination)

                def generate_stub(model, upstream, url, staged):
                    staged.mkdir()
                    return {}

                with contextlib.ExitStack() as stack:
                    stack.enter_context(patch("scripts.build.ROOT", root))
                    stack.enter_context(patch("scripts.build.load_model", return_value=load_model()))
                    stack.enter_context(patch("scripts.build.fetch_provider", return_value=("fixture", b"")))
                    stack.enter_context(patch("scripts.build.generate", side_effect=generate_stub))
                    stack.enter_context(patch("scripts.validate.validate_dist", return_value={}))
                    stack.enter_context(patch.object(Path, "rename", fail_swap))
                    with self.assertRaises((OSError, RuntimeError)):
                        build("https://example.com/release")
                saved = root / (".cache/dist-previous/marker" if restore_fails else "dist/marker")
                self.assertEqual(saved.read_text(), "previous working output")

    def test_sync_validates_then_backs_up_and_replaces_only_selected_file(self):
        content = (ROOT / "dist/clash-verge/routing.js").read_bytes()
        expected = hashlib.sha256(content).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "global.js"
            target.write_text("old script")
            self.assertTrue(install_script(target, content, expected))
            self.assertEqual(target.read_bytes(), content)
            self.assertEqual(target.with_suffix(".js.bak").read_text(), "old script")
            self.assertFalse(install_script(target, content, expected))
            with self.assertRaises(ValueError):
                install_script(target, b"truncated", expected)
            self.assertEqual(target.read_bytes(), content)
            bad = b"function main(config) { config.dns={enable:false}; return config; }"
            with self.assertRaises(ValueError):
                install_script(target, bad, hashlib.sha256(bad).hexdigest())
            self.assertEqual(target.read_bytes(), content)
            self.assertEqual(target.with_suffix(".js.bak").read_text(), "old script")

    def test_first_and_repeat_publish_to_a_local_bare_remote(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".cache") as temporary:
            root = Path(temporary)
            remote, repo = root / "remote.git", root / "source"
            subprocess.run(["git", "init", "--bare", str(remote)], capture_output=True, check=True)
            subprocess.run(["git", "init", "-b", "main", str(repo)], capture_output=True, check=True)
            (repo / "source.txt").write_text("source must not be published")
            git(repo, "add", ".")
            git(repo, "-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "-m", "source")
            git(repo, "remote", "add", "origin", str(remote))
            first = publish(repo, ROOT / "dist")
            self.assertRegex(first, r"^[0-9a-f]{40}$")
            self.assertEqual(publish(repo, ROOT / "dist"), "unchanged")
            names = git(remote, "ls-tree", "-r", "--name-only", "release").stdout.splitlines()
            self.assertIn("shadowrocket/config.conf", names)
            self.assertNotIn("source.txt", names)
            # A client holding an older config still needs its immutable rule URLs.
            git(repo, "fetch", "origin", "release")
            git(repo, "switch", "--detach", "FETCH_HEAD")
            archived = repo / "rules/old-snapshot/retained.list"
            archived.parent.mkdir(parents=True)
            archived.write_text("DOMAIN,old.example.com\n")
            git(repo, "add", ".")
            git(repo, "-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "-m", "old snapshot")
            git(repo, "push", "origin", "HEAD:release")
            git(repo, "switch", "main")
            publish(repo, ROOT / "dist")
            names = git(remote, "ls-tree", "-r", "--name-only", "release").stdout.splitlines()
            self.assertIn("rules/old-snapshot/retained.list", names)


if __name__ == "__main__":
    unittest.main()
