"""Publish validated dist with one normal Git push; retain old rule snapshots."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.model import ROOT
from scripts.validate import validate_dist


def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args], text=True, encoding="utf-8",
                          capture_output=True, check=check)


def publish(repo, dist):
    manifest = validate_dist(dist)
    source_revision = git(repo, "rev-parse", "HEAD").stdout.strip()
    remote = git(repo, "ls-remote", "--exit-code", "--heads", "origin", "release", check=False)
    if remote.returncode not in {0, 2}:
        raise RuntimeError("无法查询发布分支；未执行发布")
    if remote.returncode == 0:
        git(repo, "fetch", "origin", "refs/heads/release")
        base = git(repo, "rev-parse", "FETCH_HEAD").stdout.strip()
    else:
        base = "HEAD"
    staging = repo / ".cache"
    staging.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="publish-", dir=staging) as temporary:
        worktree = Path(temporary).resolve() / "tree"
        if staging.resolve() not in worktree.parents:
            raise ValueError("发布临时目录越界")
        git(repo, "worktree", "add", "--detach", str(worktree), base)
        try:
            if remote.returncode == 2:
                git(worktree, "switch", "--orphan", "routing-" + Path(temporary).name)
            for name in ["manifest.json", *manifest["files"]]:
                destination = worktree / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(dist / name, destination)
            git(worktree, "add", "--all")
            if git(worktree, "diff", "--cached", "--quiet", check=False).returncode == 0:
                return "unchanged"
            git(worktree, "-c", "user.name=github-actions[bot]", "-c",
                "user.email=41898282+github-actions[bot]@users.noreply.github.com", "commit", "-m",
                f"Build routing {manifest['build']} from {source_revision}")
            git(worktree, "push", "origin", "HEAD:refs/heads/release")
            return git(worktree, "rev-parse", "HEAD").stdout.strip()
        finally:
            git(repo, "worktree", "remove", "--force", str(worktree))


if __name__ == "__main__":
    print(publish(ROOT, ROOT / "dist"))
