"""A synchronous main(config) compatible with both clients' script overrides."""
import json
from pathlib import Path


def render(model, version):
    data = {key: model[key] for key in ("proxy-groups", "rule-providers", "rules")}
    template = Path(__file__).with_name("mihomo.js").read_text(encoding="utf-8")
    return template.replace("__VERSION__", version).replace(
        "__DATA__", json.dumps(data, ensure_ascii=False, indent=2)
    ).replace("__UDP__", json.dumps(model["settings"]["udp"]))

