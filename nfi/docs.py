"""Fill number markers in the docs from data/out/headline.json.

Marker: <!--n:key:fmt-->anything<!--/n-->
Formats: int | sint | pct | spct | x | 1 | s1 | 2 | s2 | m.
"""
import json, re, sys
from .net import ROOT

PAT = re.compile(r"<!--n:([a-zA-Z0-9_.]+):?([a-z0-9]*)-->(.*?)<!--/n-->", re.S)


def fmt(v, f):
    if v is None:
        return "n/a"
    if f == "int":
        return f"{v:,.0f}"
    if f == "sint":
        return f"{v:+,.0f}"
    if f == "pct":
        return f"{v:.2f}%"
    if f == "d4":
        return f"{v:,.4f}"
    if f == "yn":
        return "yes" if v else "no"
    if f == "pct3":
        return f"{v:.3f}".rstrip("0").rstrip(".") + "%"
    if f == "spct":
        return f"{v:+.2f}%"
    if f == "x":
        return f"{v:,.0f}×" if v >= 10 else f"{v:.1f}×"
    if f == "m":
        return f"{v / 1e6:,.2f}M"
    if f == "1":
        return f"{v:.1f}"
    if f == "s1":
        return f"{v:+.1f}"
    if f == "2":
        return f"{v:.2f}"
    if f == "s2":
        return f"{v:+.2f}"
    return str(v)


def get(h, key):
    cur = h
    for part in key.split("."):
        cur = cur.get(part) if isinstance(cur, dict) else None
    return cur


def render(text, head):
    return PAT.sub(lambda m: f"<!--n:{m.group(1)}:{m.group(2)}-->{fmt(get(head, m.group(1)), m.group(2))}<!--/n-->", text)


if __name__ == "__main__":
    head = json.loads((ROOT / "data" / "out" / "headline.json").read_text())
    for name in sys.argv[1:] or ["README.md", "THESIS.md", "METHOD.md", "LONG_TERM_PLAN.md"]:
        p = ROOT / name
        p.write_text(render(p.read_text(), head))
    print("docs rendered")
