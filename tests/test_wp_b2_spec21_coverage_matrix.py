"""WP-B2 — `CHECK-B2-08`: bảng đối chiếu §21 → test phải ĐẦY ĐỦ và không được trôi.

Một bảng đối chiếu viết tay là loại tài liệu hỏng âm thầm nhanh nhất: spec đổi một dòng,
một test bị đổi tên, và bảng vẫn "xanh" trong khi nó nói về một thế giới không còn tồn tại.
Module này biến bảng thành một hợp đồng kiểm được:

1. Tập requirement trong bảng == tập gạch đầu dòng §21.1–§21.4 của
   `docs/spec/03_BACKTEST_SPEC_V2_1_5.md`, so NGUYÊN VĂN. Thêm/bớt/sửa một câu trong spec
   mà không cập nhật bảng -> đỏ.
2. Mọi trạng thái thuộc `{TESTED, NOT_APPLICABLE, MIXED}`.
3. Mọi tên test được viện dẫn TỒN TẠI trong `tests/` (đọc bằng AST, không grep).
4. `NOT_APPLICABLE` / `MIXED` phải mang lý do thật, không được để trống.
5. Không requirement nào rơi vào im lặng: không hàng nào thiếu cả test lẫn lý do.

Cùng khuôn với `test_b3_03_reason_code_catalogue_matches_the_spec_text` của WP-B3: đối
chiếu artifact với CHÍNH văn bản spec, không với một bản chép tay thứ hai.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SPEC = REPO / "docs" / "spec" / "03_BACKTEST_SPEC_V2_1_5.md"
CONVENTIONS = REPO / "docs" / "CONVENTIONS.md"
TESTS_DIR = REPO / "tests"

TABLE_HEADING = "## Đối chiếu requirement Backtest §21 → test (WP-B2)"
VALID_STATUS = {"TESTED", "NOT_APPLICABLE", "MIXED"}

#: `tests/<file>::<test_name>` hoặc `::<test_name>` (viện dẫn tiếp theo trong cùng ô).
_REF = re.compile(r"`(?:(tests/[A-Za-z0-9_./]+\.py))?::([A-Za-z0-9_]+)`")


def spec_bullets() -> list[tuple[str, str]]:
    """(mục, nguyên văn) mọi gạch đầu dòng của §21.1–§21.4."""
    out, section = [], None
    for line in SPEC.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^###\s+(21\.\d)\s", line)
        if m:
            section = m.group(1)
            continue
        if re.match(r"^##\s+(?!#)", line) and not line.startswith("## 21"):
            section = None
        if section and line.startswith("- "):
            out.append((section, line[2:].strip()))
    return out


def table_rows() -> list[dict]:
    text = CONVENTIONS.read_text(encoding="utf-8")
    assert TABLE_HEADING in text, "không tìm thấy mục bảng đối chiếu trong CONVENTIONS.md"
    body = text.split(TABLE_HEADING, 1)[1]
    rows = []
    for line in body.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 5 or cells[0] in ("#", "---"):
            continue
        rows.append({"idx": cells[0], "section": cells[1], "requirement": cells[2],
                     "status": cells[3], "evidence": cells[4]})
    return rows


def declared_test_names() -> set[str]:
    """Mọi hàm `test_*` khai báo trong `tests/` — đọc bằng AST, không phải bằng grep."""
    names = set()
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    and node.name.startswith("test_"):
                names.add(node.name)
                names.add(f"{path.relative_to(REPO).as_posix()}::{node.name}")
    return names


ROWS = table_rows()
BULLETS = spec_bullets()
DECLARED = declared_test_names()


def test_b2_08a_table_covers_every_section_21_bullet_verbatim():
    """Tập requirement trong bảng == tập gạch đầu dòng §21, so nguyên văn."""
    assert BULLETS, "không đọc được gạch đầu dòng nào từ §21 — parser hỏng"
    assert len(ROWS) == len(BULLETS), \
        f"bảng có {len(ROWS)} hàng, §21 có {len(BULLETS)} gạch đầu dòng"
    for row, (section, text) in zip(ROWS, BULLETS):
        assert row["section"] == section, (row["idx"], row["section"], section)
        assert row["requirement"] == text, (
            f"hàng {row['idx']} lệch nguyên văn spec:\n  bảng: {row['requirement']}\n"
            f"  spec: {text}")
    assert {r["requirement"] for r in ROWS} == {b for _s, b in BULLETS}


def test_b2_08b_table_is_indexed_from_one_without_gaps():
    assert [r["idx"] for r in ROWS] == [str(i) for i in range(1, len(BULLETS) + 1)]


@pytest.mark.parametrize("row", ROWS, ids=[r["idx"] for r in ROWS])
def test_b2_08c_every_row_declares_a_valid_status(row):
    assert row["status"] in VALID_STATUS, (row["idx"], row["status"])


@pytest.mark.parametrize("row", ROWS, ids=[r["idx"] for r in ROWS])
def test_b2_08d_every_referenced_test_exists(row):
    """Mọi tên test viện dẫn phải tồn tại — bảng không được trỏ vào hư không."""
    refs = _REF.findall(row["evidence"])
    for file_part, name in refs:
        if file_part:
            key = f"{file_part}::{name}"
            assert key in DECLARED, f"hàng {row['idx']}: không có {key}"
        else:
            assert name in DECLARED, f"hàng {row['idx']}: không có test tên {name}"


@pytest.mark.parametrize("row", ROWS, ids=[r["idx"] for r in ROWS])
def test_b2_08e_no_requirement_falls_into_silence(row):
    """`TESTED` phải có ít nhất một test; `NOT_APPLICABLE`/`MIXED` phải có lý do thật."""
    refs = _REF.findall(row["evidence"])
    if row["status"] == "TESTED":
        assert refs, f"hàng {row['idx']}: TESTED nhưng không viện dẫn test nào"
    if row["status"] == "NOT_APPLICABLE":
        assert not refs, f"hàng {row['idx']}: NOT_APPLICABLE thì không được viện dẫn test"
    if row["status"] == "MIXED":
        assert refs, f"hàng {row['idx']}: MIXED phải có phần CÓ test"
        assert "NOT_APPLICABLE" in row["evidence"], \
            f"hàng {row['idx']}: MIXED phải nói rõ phần nào NOT_APPLICABLE và vì sao"
    if row["status"] in ("NOT_APPLICABLE", "MIXED"):
        # Lý do phải nói được vì sao, và nói nó thuộc về đâu — một dòng "không áp dụng"
        # trống rỗng chính là hình thức im lặng mà CHECK-B2-08 cấm.
        assert len(row["evidence"]) >= 120, f"hàng {row['idx']}: lý do quá mỏng để kiểm chứng"


def test_b2_08f_every_wp_b2_test_module_is_referenced_by_the_table():
    """Chiều ngược lại: test do WP-B2 viết phải có đường về một requirement §21.

    Không có phép kiểm này thì một test WP-B2 có thể tồn tại mà không đóng requirement nào
    — đúng kiểu 'tăng số test' mà task file cấm.
    """
    evidence = " ".join(r["evidence"] for r in ROWS)
    modules = {p.relative_to(REPO).as_posix() for p in TESTS_DIR.glob("test_wp_b2_spec21_*.py")}
    modules -= {"tests/test_wp_b2_spec21_coverage_matrix.py"}   # chính bảng, không phải §21
    assert modules, "không tìm thấy module test nào của WP-B2"
    for mod in sorted(modules):
        assert mod in evidence, f"{mod} không được bảng đối chiếu viện dẫn"

    referenced = {name for _f, name in _REF.findall(evidence)}
    for mod in sorted(modules):
        tree = ast.parse((REPO / mod).read_text(encoding="utf-8"), filename=mod)
        declared = {n.name for n in ast.walk(tree)
                    if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")}
        missing = declared - referenced
        assert not missing, f"{mod}: test không gắn với requirement §21 nào: {sorted(missing)}"
