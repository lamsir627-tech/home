#!/usr/bin/env python3
"""Snapshot a UTF-8 script and index every physical line without text loss.

Classifications are candidates, not editorial decisions: every nonblank unit
requires review. Offsets count Unicode characters after UTF-8 BOM decoding;
the snapshot and its SHA-256 retain the original bytes, including BOM and CRLF.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys


DIGITS = {c: n for n, chars in enumerate(("零〇", "一", "二两", "三", "四", "五", "六", "七", "八", "九")) for c in chars}
EPISODE = re.compile(r"^(?:第\s*([0-9０-９零〇一二两三四五六七八九十百千万]+)\s*[集话]|episode\s+(\d+))(?=$|[\s:：、.．\-—·]|[^A-Za-z0-9])", re.I)
SCENE = re.compile(r"^(?:\d+\s*[-—.]\s*\d+(?=\s|[:：]|$)|(?:场景|场次)\s*[:：]\s*\S|(?:场景|场次|第)\s*[0-9零〇一二两三四五六七八九十百]+\s*(?:场|幕)?(?=\s|[:：、.]|$)|(?:内景|外景|内外景|INT\.|EXT\.|INT\./EXT\.)(?=\s|[:：]|$))", re.I)
ROLE_LINE = re.compile(r"^([^:：\r\n]{1,48})[:：](.*)$")
NON_TEXT_CONTROLS = re.compile(r"[\x00-\x08\x0b\x0e-\x1f\x7f]")
META_KEYS = {"标题", "剧名", "主要人物", "人物", "人物介绍", "人物小传", "角色", "角色介绍", "角色表", "人物表", "出场人物", "出场角色", "时间", "地点", "场景", "场次", "时长", "集数", "简介", "故事梗概", "剧情梗概", "备注", "说明", "设定", "作者", "title", "cast", "characters", "time", "location"}
CAST_KEYS = {"主要人物", "人物", "角色", "人物介绍", "人物小传", "角色介绍", "角色表", "人物表", "cast", "characters"}
SUBTITLE_KEYS = {"字幕", "屏幕文字", "屏显文字", "字卡", "字幕参考", "subtitle", "subtitles", "caption"}
TRANSLATION_KEYS = {"中文", "英文", "中译", "英译", "译文", "translation", "zh", "en", "chinese", "english"}
ACTION_KEYS = {"画面", "动作", "镜头", "音效", "环境音", "音乐", "转场", "action", "sfx", "bgm"}
NARRATION_KEYS = {"旁白", "解说", "narrator", "narration"}
VO_KEYS = {"vo", "v.o.", "v.o", "画外音", "内心独白", "os", "o.s.", "o.s"}


def episode_number(value: str) -> str:
    """Convert an explicit original episode number; never invent numbering."""
    if value.isdecimal():
        return str(int(value))
    if all(c in DIGITS for c in value):
        return str(int("".join(str(DIGITS[c]) for c in value)))
    total = section = number = 0
    for char in value:
        if char in DIGITS:
            number = DIGITS[char]
        elif char == "万":
            total += (section + number or 1) * 10000
            section = number = 0
        else:
            multiplier = {"十": 10, "百": 100, "千": 1000}[char]
            section += (number or 1) * multiplier
            number = 0
    return str(total + section + number)


def display_content(raw: str) -> tuple[str, int]:
    """Return trimmed line content and its exact start inside the raw line."""
    body = raw.rstrip("\r\n")
    left = len(body) - len(body.lstrip())
    return body.strip(), left


def heading_content(content: str) -> str:
    candidate = re.sub(r"^#{1,6}\s+", "", content)
    if candidate.startswith("**") and candidate.endswith("**"):
        candidate = candidate[2:-2].strip()
    return candidate


def episode_of(raw: str) -> str | None:
    content, _ = display_content(raw)
    match = EPISODE.match(heading_content(content))
    return episode_number(match.group(1) or match.group(2)) if match else None


def plausible_speaker(label: str) -> bool:
    base = re.split(r"[（(\[]", label, maxsplit=1)[0].strip()
    if not base or base.isdecimal():
        return False
    # Do not turn timestamps, URLs, notes, or whole sentences into speakers.
    return bool(re.fullmatch(r"[A-Za-z\u3400-\u9fff][A-Za-z0-9\u3400-\u9fff ·.'’_\-]{0,31}", base)) and base.lower() not in {"http", "https", "file", "ftp"}


def classify(raw: str, start: int, in_cast: bool) -> dict:
    content, content_start = display_content(raw)
    fields = dict(kind="unclassified", speaker=None, spoken_text=None,
                  spoken_start=None, spoken_end=None, audible=None,
                  reviewed=False, pair_id=None, note="未分类原文；需判定内容类型和是否属于主声轨。")
    if not content:
        fields.update(kind="blank", audible=False, reviewed=True, note="空白行；原始空白及换行已保留。")
        return fields
    heading = heading_content(content)
    if episode_of(raw) is not None or SCENE.match(heading) or heading in {"正文", "剧本正文", "剧情开始"}:
        fields.update(kind="heading", audible=False, note="集界或场头候选；需人工核对原文边界。")
        return fields
    match = ROLE_LINE.match(content)
    key = (match.group(1) if match else heading).strip().lower()
    if key in META_KEYS or key in CAST_KEYS:
        fields.update(kind="metadata", audible=False, note="说明或人物资料候选；需复核，不作为角色对白自动确认。")
        return fields
    if in_cast:
        fields.update(kind="metadata", audible=None, note="人物资料段候选；若本行已进入正文，须重新分类并核定主声轨。")
        return fields
    if key in SUBTITLE_KEYS or re.match(r"^[【\[]\s*(?:字幕|屏幕文字|屏显文字|字卡|字幕参考)\s*(?:[】\]]|[:：])", content):
        fields.update(kind="subtitle", audible=False, note="字幕候选；需核实是否另有对应口播，不据此猜测双语配对。")
        return fields
    if key in TRANSLATION_KEYS:
        fields.update(kind="translation", audible=None, note="语言或译文标签候选；主声轨与双语配对需人工核定。")
        return fields
    if key in ACTION_KEYS or content.startswith(("△", "▲")) or re.match(r"^[【\[]\s*(?:画面|动作|音效|镜头)\s*[】\]]", content):
        fields.update(kind="action", audible=False, note="画面、动作或声音说明候选；需检查其中是否嵌入真实台词。")
        return fields
    if not match:
        return fields
    role = match.group(1).strip()
    lower_role = role.lower()
    if not plausible_speaker(role):
        return fields
    if re.match(r"\s*(?:男|女)(?:性)?\s*[,，、/／]\s*\d+\s*岁", match.group(2)):
        fields.update(kind="metadata", audible=None, note="角色年龄资料候选；需复核是否为人物介绍或实际对白。")
        return fields
    kind = "dialogue"
    if lower_role in NARRATION_KEYS:
        kind = "narration"
    elif lower_role in VO_KEYS or re.search(r"[（(]\s*(?:vo|v\.o\.?|os|o\.s\.?|画外音|内心)\s*[）)]", role, re.I):
        kind = "vo"
    body = match.group(2)
    body_left = len(body) - len(body.lstrip())
    spoken = body.strip()
    if not spoken:
        fields["note"] = "只有角色标签，未找到同行台词；需检查下一行并重新分类。"
        return fields
    spoken_start = start + content_start + match.start(2) + body_left
    fields.update(kind=kind, speaker=role, spoken_text=spoken,
                  spoken_start=spoken_start, spoken_end=spoken_start + len(spoken),
                  audible=True,
                  note="有声候选；保留原角色标记。需复核角色、括号动作、主声轨及同行多发言者；未自动确认双语配对。")
    return fields


def make_ledger(text: str, source_bytes: bytes, snapshot: Path) -> dict:
    # Explicit CR/LF splitting avoids treating Unicode line separators as
    # physical line boundaries and retains mixed newline styles exactly.
    lines = [m.group() for m in re.finditer(r"[^\r\n]*(?:\r\n|\r|\n|$)", text) if m.group()]
    current_episode = None if any(episode_of(raw) is not None for raw in lines) else "1"
    current_scene = None
    in_cast = False
    units = []
    start = 0
    for order, raw in enumerate(lines, 1):
        content, _ = display_content(raw)
        heading = heading_content(content)
        episode = episode_of(raw)
        if episode is not None:
            current_episode, current_scene, in_cast = episode, None, False
        elif SCENE.match(heading):
            current_scene, in_cast = content, False
        elif heading in {"正文", "剧本正文", "剧情开始"}:
            in_cast = False
        fields = classify(raw, start, in_cast)
        unit = dict(id=f"U{order:06d}", order=order, start=start,
                    end=start + len(raw), raw=raw, episode=current_episode,
                    scene=current_scene, **fields)
        units.append(unit)
        key_match = ROLE_LINE.match(content)
        key = (key_match.group(1) if key_match else heading).strip().lower()
        if key in CAST_KEYS:
            # A populated scene cast list describes this line only. An empty
            # cast heading can introduce subsequent character descriptions.
            in_cast = key_match is None or not key_match.group(2).strip()
        start = unit["end"]
    if start != len(text) or "".join(unit["raw"] for unit in units) != text:
        raise ValueError("Internal coverage check failed; no output was written.")
    for unit in units:
        if unit["spoken_text"] is not None and text[unit["spoken_start"]:unit["spoken_end"]] != unit["spoken_text"]:
            raise ValueError(f"Internal spoken-text boundary check failed for {unit['id']}.")
    return dict(schema_version=1, source=dict(path=str(snapshot),
                sha256=hashlib.sha256(source_bytes).hexdigest(), char_count=len(text)), units=units)


def build(source: Path, out_dir: Path) -> dict:
    source = source.expanduser().resolve(strict=True)
    if not source.is_file() or source.suffix.lower() not in {".txt", ".md"}:
        raise ValueError("--source must be an existing UTF-8 .txt or .md file.")
    source_bytes = source.read_bytes()
    try:
        text = source_bytes.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("Source is not valid UTF-8; convert it explicitly before indexing.") from exc
    if NON_TEXT_CONTROLS.search(text):
        raise ValueError("Source contains binary/control bytes; use a plain UTF-8 text export.")
    if not text.strip():
        raise ValueError("Source is empty or contains only whitespace.")
    out_dir = out_dir.expanduser().resolve()
    snapshot = out_dir / "source.snapshot.txt"
    ledger_path = out_dir / "source-ledger.json"
    if any(path.exists() or path.is_symlink() for path in (snapshot, ledger_path)):
        raise ValueError("Refusing to overwrite an existing snapshot or ledger; use a new --out-dir.")
    ledger = make_ledger(text, source_bytes, snapshot)
    ledger_bytes = (json.dumps(ledger, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    out_dir.mkdir(parents=True, exist_ok=True)
    created = []
    try:
        for path, data in ((snapshot, source_bytes), (ledger_path, ledger_bytes)):
            with path.open("xb") as stream:
                created.append(path)
                stream.write(data)
    except OSError:
        # Only clean up files created by this invocation, never preexisting data.
        for path in reversed(created):
            path.unlink(missing_ok=True)
        raise
    counts = Counter(unit["kind"] for unit in ledger["units"])
    return dict(snapshot=str(snapshot), ledger=str(ledger_path),
                char_count=len(text), unit_count=len(ledger["units"]),
                review_required=sum(not unit["reviewed"] for unit in ledger["units"]),
                kind_counts=dict(counts), coverage="exact", classification="candidates_require_review")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="UTF-8 .txt or .md source")
    parser.add_argument("--out-dir", required=True, type=Path, help="Work directory without a previous snapshot or ledger")
    args = parser.parse_args()
    try:
        result = build(args.source, args.out_dir)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
