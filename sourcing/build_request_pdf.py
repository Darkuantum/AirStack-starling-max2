#!/usr/bin/env python3
"""Render request-list.md to request-list.html (then print it to PDF with Chrome).

Needs the `markdown` package. Usage, from this directory:
  python3 build_request_pdf.py
  google-chrome --headless=new --disable-gpu --no-pdf-header-footer \
      --print-to-pdf=request-list.pdf "file://$PWD/request-list.html"
"""
import pathlib
import re

import markdown

HERE = pathlib.Path(__file__).parent
src = (HERE / "request-list.md").read_text()

# Links into the repo don't work in a shared PDF: keep their text, drop the link.
src = re.sub(r"\[([^\]]+)\]\((?!https?://)[^)]+\)", r"\1", src)
# python-markdown needs a blank line before a list that follows a paragraph line.
src = re.sub(r"(?m)^((?![-*] ).*\S.*)\n(- )", r"\1\n\n\2", src)

body = markdown.markdown(src, extensions=["tables", "fenced_code"])

# Row styles: "↳" rows are alternatives to the item above, "§" rows are group
# headings (spanning the table), and rows with an empty first cell are totals.
body = body.replace("<tr>\n<td>↳</td>", '<tr class="alt">\n<td>↳</td>')
body = re.sub(r"<tr>\n<td>§</td>\n<td>(.*?)</td>\n((?:<td></td>\n)*)</tr>",
              lambda m: f'<tr class="group"><td colspan="{2 + m.group(2).count("<td>")}">{m.group(1)}</td></tr>',
              body)
body = body.replace("<tr>\n<td></td>", '<tr class="sum">\n<td></td>')
# Items already in the owner's cart: badge the marker and tint the whole row.
body = body.replace("<strong>IN CART</strong>", '<span class="cart">IN CART</span>')
body = re.sub(r'<tr(?: class="(\w+)")?>((?:(?!</tr>).)*?class="cart")',
              lambda m: f'<tr class="{(m.group(1) or "") + " incart"}">{m.group(2)}', body, flags=re.S)

CSS = """
@page { size: A4 landscape; margin: 9mm 11mm 8mm; }
body { font-family: "DejaVu Sans", Arial, sans-serif; font-size: 7.0pt; color: #1b1f24; line-height: 1.2; }
h1, h2 { font-size: 13pt; margin: 0 0 1.5mm; color: #1f4e79; border: 0; padding: 0; }
h2 { break-before: page; }
p, ul { margin: 1mm 0; }
li { margin: 0.3mm 0; }
table { border-collapse: collapse; width: 100%; margin: 1.5mm 0; }
th, td { border: 1px solid #c9d1db; padding: 0.55mm 1.2mm; vertical-align: top; text-align: left; }
th { background: #eef2f6; }
tr { break-inside: avoid; }
tr.alt td { background: #f7f8fa; color: #4a5260; font-size: 6.9pt; }
tr.alt td:first-child { text-align: right; padding-left: 3mm; }
tr.group td { background: #eef2f6; font-weight: bold; padding-top: 1.2mm; }
tr.sum td { border-left-color: transparent; border-right-color: transparent; }
tr.sum td:nth-last-child(-n+3) { border-left-color: #c9d1db; border-right-color: #c9d1db; }
table { table-layout: fixed; }
th, td { box-sizing: border-box; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 7pt; }
a { color: #1f5fa8; text-decoration: none; }
tr.incart td { background: #e6f4ea; }
.cart { display: inline-block; background: #1e7e34; color: #fff; font-weight: bold; font-size: 6.4pt; padding: 0 1.2mm; border-radius: 1mm; margin-right: 1mm; }
table:first-of-type th:nth-child(1) { width: 2.5%; } table:first-of-type th:nth-child(2) { width: 24%; } table:first-of-type th:nth-child(3) { width: 26%; } table:first-of-type th:nth-child(4) { width: 5.5%; } table:first-of-type th:nth-child(5) { width: 7.5%; } table:first-of-type th:nth-child(6) { width: 6.5%; } table:first-of-type th:nth-child(7) { width: 28%; }
table:last-of-type th:nth-child(1) { width: 2.5%; } table:last-of-type th:nth-child(2) { width: 28%; } table:last-of-type th:nth-child(3) { width: 17%; } table:last-of-type th:nth-child(4) { width: 4%; } table:last-of-type th:nth-child(5) { width: 8.5%; } table:last-of-type th:nth-child(6) { width: 8%; } table:last-of-type th:nth-child(7) { width: 7%; } table:last-of-type th:nth-child(8) { width: 25%; }
"""

html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Purchase request — Starling 2 Max phase 1 and Jetson Orin NX</title>
<style>{CSS}</style></head><body>
{body}
</body></html>
"""
(HERE / "request-list.html").write_text(html)
print("wrote request-list.html")
