"""C13 REVIEW 2, session 8c49c4d3 — this session's OWN reader for arXiv 2503.18813v2.

Imports nothing from src/. Resolves each table's appendix from the document
structure (the <h2 class="ltx_title_appendix"> of its enclosing <section>),
never from anybody's say-so. Handles LaTeXML's span-tabulars and rowspan.
"""
import re
import hashlib
from html.parser import HTMLParser

RAW = open('camel_paper_v2.html', 'rb').read()
H = RAW.decode('utf-8')
PM = '±'


class SpanTable(HTMLParser):
    """Collect ltx_tr / ltx_td structure from LaTeXML span-tabulars."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.rows = []
        self.cur = None
        self.cell = None
        self.cellspan = 1

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cl = a.get('class', '')
        self.stack.append((tag, cl))
        cls = cl.split()
        if 'ltx_tr' in cls:
            self.cur = []
        elif 'ltx_td' in cls and self.cur is not None:
            self.cell = []
            self.cellspan = int(a.get('rowspan', '1') or 1)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                cl = self.stack[i][1]
                del self.stack[i:]
                break
        else:
            return
        cls = cl.split()
        if 'ltx_td' in cls and self.cell is not None:
            self.cur.append((''.join(self.cell), self.cellspan))
            self.cell = None
        elif 'ltx_tr' in cls and self.cur is not None:
            self.rows.append(self.cur)
            self.cur = None

    def handle_data(self, d):
        if self.cell is not None:
            self.cell.append(d)


def clean(s):
    """LaTeXML emits math twice (visible + alt). Collapse adjacent duplicate tokens."""
    s = s.replace('\\pm', ' ' + PM + ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    toks = s.split()
    out = []
    for t in toks:
        if out and out[-1] == t:
            continue
        out.append(t)
    s = ' '.join(out)
    # collapse "62.5 % ± 23.7 62.5 ± 23.7" -> keep the first rendering
    m = re.match(r'^(-?[\d.]+\s*%?\s*' + PM + r'\s*[\d.]+)\b', s)
    if m:
        rest = s[m.end():].strip()
        nums_first = re.findall(r'-?[\d.]+', m.group(1))
        nums_rest = re.findall(r'-?[\d.]+', rest)
        if nums_rest and nums_rest[:len(nums_first)] == nums_first:
            return m.group(1).strip()
    return s


def strip(frag):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', frag)).strip()


def figure_span(fid):
    m = re.search(r'<figure[^>]*id="%s"[^>]*>' % re.escape(fid), H)
    st = m.start()
    en = H.find('</figure>', st)
    return H[st:en]


def appendix_of(fid):
    sec = fid.split('.')[0]
    sm = re.search(r'<section[^>]*id="%s"[^>]*>(.{0,4000})' % re.escape(sec), H, re.S)
    if not sm:
        return None
    tm = re.search(r'<h2[^>]*ltx_title_appendix[^>]*>(.*?)</h2>', sm.group(1), re.S)
    return strip(tm.group(1)) if tm else None


def table(fid):
    frag = figure_span(fid)
    cm = re.search(r'<figcaption[^>]*>(.*?)</figcaption>', frag, re.S)
    cap = strip(cm.group(1)) if cm else None
    p = SpanTable()
    p.feed(frag)
    grid = []
    carry = {}
    for r in p.rows:
        row = []
        ci = 0
        while ci in carry and carry[ci][0] > 0:
            row.append(carry[ci][1])
            carry[ci] = (carry[ci][0] - 1, carry[ci][1])
            ci += 1
        for (raw, rs) in r:
            row.append(clean(raw))
            if rs > 1:
                carry[ci] = (rs - 1, clean(raw))
            ci += 1
            while ci in carry and carry[ci][0] > 0:
                row.append(carry[ci][1])
                carry[ci] = (carry[ci][0] - 1, carry[ci][1])
                ci += 1
        grid.append(row)
    return cap, appendix_of(fid), grid


if __name__ == '__main__':
    print('SHA-256:', hashlib.sha256(RAW).hexdigest(), ' bytes:', len(RAW))
    for fid, name in [('A2.T4', 'Table 4'), ('A2.T2', 'Table 2'),
                      ('A3.T5', 'Table 5'), ('A3.T6', 'Table 6'), ('A3.T7', 'Table 7')]:
        cap, app, grid = table(fid)
        print('\n' + '=' * 110)
        print('%s  id=%s  APPENDIX (resolved from document structure) = %s' % (name, fid, app))
        print('CAPTION: %s' % cap)
        print('-' * 110)
        for r in grid:
            print(' || '.join(r))
