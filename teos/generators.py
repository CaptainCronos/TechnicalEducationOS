"""Deterministic physical-format generators for rendered text."""

from __future__ import annotations

import html
import io
import textwrap
import zipfile
from typing import Any

GENERATOR_IDS = ("markdown", "html", "docx", "pdf")


def _zip_entry(name: str, content: bytes) -> tuple[zipfile.ZipInfo, bytes]:
    entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    entry.compress_type = zipfile.ZIP_DEFLATED
    entry.external_attr = 0o600 << 16
    return entry, content


def generate_markdown(content: str, theme: dict[str, Any]) -> bytes:
    """Encode a rendered Markdown document without changing its meaning."""
    del theme
    return content.encode("utf-8")


def generate_html(content: str, theme: dict[str, Any]) -> bytes:
    """Wrap rendered text in deterministic, themed HTML."""
    tokens = theme["tokens"]
    document = (
        "<!doctype html>\n"
        f'<html lang="{html.escape(theme.get("_locale", "en"))}">'
        '<head><meta charset="utf-8">\n'
        "<title>TEOS artifact</title>\n"
        "<style>"
        "body{white-space:pre-wrap;"
        f"background:{tokens['background']};color:{tokens['foreground']};"
        f"font-family:{tokens['font_family']};}}"
        f"a{{color:{tokens['accent']};}}"
        "</style></head><body>"
        f"{html.escape(content)}"
        "</body></html>\n"
    )
    return document.encode("utf-8")


def generate_docx(content: str, theme: dict[str, Any]) -> bytes:
    """Create a minimal deterministic OOXML word-processing document."""
    del theme
    paragraphs = []
    for line in content.splitlines():
        escaped = html.escape(line)
        paragraphs.append(
            '<w:p><w:r><w:t xml:space="preserve">'
            f"{escaped}</w:t></w:r></w:p>"
        )
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w='
        '"http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{''.join(paragraphs)}<w:sectPr/></w:body></w:document>"
    ).encode("utf-8")
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType='
        '"application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType='
        '"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    ).encode("utf-8")
    relationships = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns='
        '"http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type='
        '"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/></Relationships>'
    ).encode("utf-8")
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, data in (
            ("[Content_Types].xml", content_types),
            ("_rels/.rels", relationships),
            ("word/document.xml", document),
        ):
            archive.writestr(*_zip_entry(name, data))
    return output.getvalue()


def _pdf_escape(value: str) -> bytes:
    encoded = value.encode("cp1252", errors="replace")
    return encoded.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


def generate_pdf(content: str, theme: dict[str, Any]) -> bytes:
    """Create a small deterministic PDF using the built-in Helvetica font."""
    del theme
    lines = [
        wrapped_line
        for line in content.splitlines()
        for wrapped_line in (
            textwrap.wrap(
                line,
                width=100,
                break_long_words=False,
                break_on_hyphens=False,
            )
            or [""]
        )
    ]
    pages = [lines[index : index + 64] for index in range(0, len(lines), 64)]
    if not pages:
        pages = [[]]
    page_object_numbers = [4 + index * 2 for index in range(len(pages))]
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        (
            b"<< /Type /Pages /Kids ["
            + b" ".join(f"{number} 0 R".encode("ascii") for number in page_object_numbers)
            + f"] /Count {len(pages)} >>".encode("ascii")
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
    ]
    for index, page_lines in enumerate(pages):
        page_number = page_object_numbers[index]
        content_number = page_number + 1
        commands = [b"BT /F1 9 Tf 45 760 Td 11 TL"]
        for line_index, line in enumerate(page_lines):
            if line_index:
                commands.append(b"T*")
            commands.append(b"(" + _pdf_escape(line) + b") Tj")
        commands.append(b"ET")
        stream = b"\n".join(commands)
        objects.extend(
            [
                (
                    b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                    b"/Resources << /Font << /F1 3 0 R >> >> /Contents "
                    + f"{content_number} 0 R >>".encode("ascii")
                ),
                b"<< /Length "
                + str(len(stream)).encode("ascii")
                + b" >>\nstream\n"
                + stream
                + b"\nendstream",
            ]
        )
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(output)


GENERATORS = {
    "markdown": (".md", generate_markdown),
    "html": (".html", generate_html),
    "docx": (".docx", generate_docx),
    "pdf": (".pdf", generate_pdf),
}
