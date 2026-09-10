#!/usr/bin/env python3
"""
Builds two printable PDFs for manual practice of the CLRS rod-cutting
dynamic-programming algorithms:

    rod-cutting-practice-workbook.pdf   method + worked examples + 10 problems
    rod-cutting-answer-key.pdf          full traces for all 10 problems

Every number in both documents comes from cutrod_trace.py actually running
the algorithms. Nothing is hand-entered.
"""

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Frame,
                                KeepTogether, PageBreak, PageTemplate,
                                Paragraph, Preformatted, Spacer, Table,
                                TableStyle)

from cutrod_trace import MemoTrace, bottom_up, cut_list, fmt

# ------------------------------------------------------------------ styling

INK = colors.HexColor("#1a1a1a")
RULE = colors.HexColor("#8a8a8a")
LIGHT = colors.HexColor("#d8d8d8")
FILLHDR = colors.HexColor("#ececec")
ACCENT = colors.HexColor("#3b4a6b")

ss = getSampleStyleSheet()

TITLE = ParagraphStyle("TITLE", parent=ss["Title"], fontName="Helvetica-Bold",
                       fontSize=17, leading=21, textColor=ACCENT,
                       alignment=TA_LEFT, spaceAfter=2)
SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontName="Helvetica",
                     fontSize=9.5, leading=13, textColor=RULE, spaceAfter=10)
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Helvetica-Bold",
                    fontSize=13, leading=16, textColor=ACCENT,
                    spaceBefore=12, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold",
                    fontSize=10.5, leading=13, textColor=INK,
                    spaceBefore=9, spaceAfter=4)
BODY = ParagraphStyle("BODY", parent=ss["Normal"], fontName="Helvetica",
                      fontSize=9.5, leading=13, textColor=INK, spaceAfter=4)
STEP = ParagraphStyle("STEP", parent=BODY, leftIndent=22, firstLineIndent=-22,
                      spaceAfter=3)
BULL = ParagraphStyle("BULL", parent=BODY, leftIndent=14, firstLineIndent=-8,
                      spaceAfter=2)
NOTE = ParagraphStyle("NOTE", parent=BODY, fontSize=9, leading=12,
                      textColor=colors.HexColor("#444444"))
MONO = ParagraphStyle("MONO", parent=ss["Code"], fontName="Courier",
                      fontSize=8.6, leading=11, textColor=INK)
MONOB = ParagraphStyle("MONOB", parent=MONO, fontName="Courier-Bold")

PAGE_W, PAGE_H = letter
MARGIN = 0.62 * inch
CONTENT_W = PAGE_W - 2 * MARGIN


class Doc(BaseDocTemplate):
    def __init__(self, path, footer):
        BaseDocTemplate.__init__(self, path, pagesize=letter,
                                 leftMargin=MARGIN, rightMargin=MARGIN,
                                 topMargin=MARGIN, bottomMargin=MARGIN + 12,
                                 title=footer["title"], author="CMP SCI 5130")
        self.footer = footer
        frame = Frame(MARGIN, MARGIN + 12, CONTENT_W,
                      PAGE_H - 2 * MARGIN - 12, id="body",
                      leftPadding=0, rightPadding=0,
                      topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="main", frames=[frame],
                                            onPage=self._decorate)])

    def _decorate(self, canv, doc):
        canv.saveState()
        canv.setStrokeColor(LIGHT)
        canv.setLineWidth(0.5)
        canv.line(MARGIN, MARGIN + 22, PAGE_W - MARGIN, MARGIN + 22)
        canv.setFont("Helvetica", 7.5)
        canv.setFillColor(RULE)
        canv.drawString(MARGIN, MARGIN + 10, self.footer["left"])
        canv.drawRightString(PAGE_W - MARGIN, MARGIN + 10,
                             "page %d" % canv.getPageNumber())
        canv.restoreState()


# ------------------------------------------------------------- small pieces

def rule(space_before=4, space_after=6):
    t = Table([[""]], colWidths=[CONTENT_W], rowHeights=[0.6])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.6, LIGHT)]))
    return [Spacer(1, space_before), t, Spacer(1, space_after)]


def callout(title, lines, width=CONTENT_W, tint="#f4f5f8"):
    inner = [Paragraph("<b>%s</b>" % title, BODY)]
    for ln in lines:
        inner.append(Paragraph(ln, BULL))
    t = Table([[inner]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.7, RULE),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(tint)),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def code_box(text, width=CONTENT_W, size=8.4):
    st = ParagraphStyle("cb", parent=MONO, fontSize=size, leading=size + 2.4)
    t = Table([[Preformatted(text, st)]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.7, RULE),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fbfbfb")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def price_table(p, label="length i", plabel="price p[i]"):
    n = len(p)
    cw = 30
    head = [label] + [str(i) for i in range(1, n + 1)]
    row = [plabel] + [str(v) for v in p]
    t = Table([head, row], colWidths=[64] + [cw] * n, rowHeights=[16, 16])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Courier", 8.6),
        ("FONT", (0, 0), (0, -1), "Courier-Bold", 8.6),
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("BACKGROUND", (0, 0), (-1, 0), FILLHDR),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    t.hAlign = "LEFT"
    return t


def r_strip(n, values=None, label="r"):
    """The r[0..n] array strip. values=None -> blank boxes to fill in."""
    cw = 32
    head = ["index"] + [str(i) for i in range(0, n + 1)]
    if values is None:
        body = [label] + ["0"] + [""] * n
    else:
        body = [label] + [("" if v is None else str(v)) for v in values]
    t = Table([head, body], colWidths=[46] + [cw] * (n + 1),
              rowHeights=[15, 21])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Courier", 8.6),
        ("FONT", (0, 1), (-1, 1), "Courier-Bold", 9.4),
        ("FONT", (0, 0), (0, -1), "Courier-Bold", 8.6),
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("BACKGROUND", (0, 0), (-1, 0), FILLHDR),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    t.hAlign = "LEFT"
    return t


# ------------------------------------------------------- bottom-up j-blocks

JROWS = ["i", "p[i]", "j - i", "r[j-i]", "p[i]+r[j-i]", "q after"]


def j_block_parts(j, rows=None, r_j=None, s_j=None, cw=32):
    """Returns (flowables, width) for one j-block, for use in a layout row."""
    fl = j_block(j, rows, r_j, s_j, cw, wrap=False)
    return fl, 70 + cw * j


def layout_blocks(specs, cw=32, gutter=10):
    """Pack j-blocks two-up when they fit, otherwise one per row."""
    prepared = [j_block_parts(*sp, cw=cw) for sp in specs]
    out, i = [], 0
    while i < len(prepared):
        fl_a, w_a = prepared[i]
        if i + 1 < len(prepared):
            fl_b, w_b = prepared[i + 1]
            if w_a + w_b + gutter <= CONTENT_W:
                col_a = max(w_a, 152)   # room for the "r[j] = ..." caption
                if col_a + w_b + gutter > CONTENT_W:
                    col_a = w_a
                t = Table([[fl_a, "", fl_b]],
                          colWidths=[col_a, gutter,
                                     CONTENT_W - col_a - gutter])
                t.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]))
                out.append(KeepTogether([t, Spacer(1, 6)]))
                i += 2
                continue
        out.append(KeepTogether(fl_a + [Spacer(1, 6)]))
        i += 1
    return out


def j_block(j, rows=None, r_j=None, s_j=None, cw=32, wrap=True):
    """One j-block. rows=None gives a blank grid to fill in by hand."""
    data = [[lbl] + [""] * j for lbl in JROWS]
    data[0] = ["i"] + [str(i) for i in range(1, j + 1)]
    if rows is not None:
        for k, rw in enumerate(rows):
            data[1][k + 1] = str(rw["p_i"])
            data[2][k + 1] = str(rw["j_minus_i"])
            data[3][k + 1] = str(rw["r_ji"])
            data[4][k + 1] = str(rw["total"])
            data[5][k + 1] = fmt(rw["q_after"])
    tail = "r[%d] = %s     s[%d] = %s" % (j, r_j, j, s_j) if r_j is not None \
        else "r[%d] = ______    s[%d] = ______" % (j, j)
    t = Table(data, colWidths=[70] + [cw] * j,
              rowHeights=[13, 13, 13, 13, 15, 15])
    style = [
        ("FONT", (0, 0), (-1, -1), "Courier", 8.2),
        ("FONT", (0, 0), (0, -1), "Courier-Bold", 8.2),
        ("FONT", (1, 5), (-1, 5), "Courier-Bold", 8.6),
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("BACKGROUND", (0, 0), (-1, 0), FILLHDR),
        ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#f2f6fb")),
        ("BACKGROUND", (0, 5), (-1, 5), colors.HexColor("#f7f7f2")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]
    t.setStyle(TableStyle(style))
    hdr = Paragraph("<b>j = %d</b>&nbsp;&nbsp;&nbsp;<font size='8.5' "
                    "color='#555555'>(%d column%s)</font>"
                    % (j, j, "" if j == 1 else "s"), BODY)
    tailp = Paragraph("<font face='Courier' size='8.5'>%s</font>" % tail, BODY)
    if not wrap:
        return [hdr, t, tailp]
    return KeepTogether([hdr, t, tailp, Spacer(1, 6)])


def lecture_trace(blocks):
    """Reproduce the slide-style running text of the bottom-up trace."""
    out = []
    for b in blocks:
        out.append("j = %d" % b["j"])
        for rw in b["rows"]:
            out.append("        i = %d -> q = max(%s, %s)   = %s"
                       % (rw["i"], fmt(rw["q_before"]), rw["total"],
                          fmt(rw["q_after"])))
        snap = ", ".join("_" if v is None else str(v)
                         for v in b["r_snapshot"])
        out.append("    r[%d] = %-3s  ->  r = [%s]" % (b["j"], b["r_j"], snap))
        out.append("")
    return "\n".join(out).rstrip()


# --------------------------------------------------------- top-down ledgers

FRAMEHDR = ["i", "call", "returns", "p[i] + ret", "q after"]


def frame_ledger(k, rows=None, r_k=None, wrap=True,
                 snapshot=None):
    """Ledger for one MEMOIZED-CUT-ROD-AUX frame; rows=None -> blank."""
    data = [FRAMEHDR[:]]
    n_rows = k
    for idx in range(n_rows):
        if rows is None:
            data.append([str(idx + 1), "AUX(%d)" % (k - idx - 1), "", "", ""])
        else:
            rw = rows[idx]
            tag = "hit" if rw["memo_hit"] else "dive"
            data.append([str(rw["i"]), "AUX(%d)" % rw["sub_n"],
                         "%s %s" % (tag, rw["sub_val"]),
                         str(rw["total"]), fmt(rw["q_after"])])
    if k == 0:
        data.append(["-", "n == 0", "base case", "q = 0", "0"])
    cw = [20, 54, 62, 62, 50]
    t = Table(data, colWidths=cw, rowHeights=[13] + [14] * (len(data) - 1))
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Courier", 8.2),
        ("FONT", (0, 0), (-1, 0), "Courier-Bold", 8.2),
        ("FONT", (4, 1), (4, -1), "Courier-Bold", 8.4),
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("BACKGROUND", (0, 0), (-1, 0), FILLHDR),
        ("BACKGROUND", (4, 1), (4, -1), colors.HexColor("#f7f7f2")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    t.hAlign = "LEFT"
    tail = ("line 8:  r[%d] = %s" % (k, r_k) if r_k is not None
            else "line 8:  r[%d] = ______" % k)
    hdr = Paragraph("<b>Frame n = %d</b>" % k, BODY)
    tailp = Paragraph("<font face='Courier' size='8.5'>%s</font>" % tail, BODY)
    parts = [hdr, t, tailp]
    if snapshot is not None:
        parts.append(_memo_snapshot(snapshot))
    if not wrap:
        return parts
    return KeepTogether(parts + [Spacer(1, 7)])


LEDGER_W = 248


def layout_frames(specs, gutter=10):
    """Pack frame ledgers two-up. Each spec is a kwargs dict for frame_ledger."""
    ks = [sp if isinstance(sp, dict) else {"k": sp} for sp in specs]
    out, i = [], 0
    while i < len(ks):
        a = frame_ledger(wrap=False, **ks[i])
        if i + 1 < len(ks):
            b = frame_ledger(wrap=False, **ks[i + 1])
            t = Table([[a, "", b]],
                      colWidths=[LEDGER_W, gutter, CONTENT_W - LEDGER_W - gutter])
            t.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))
            out.append(KeepTogether([t, Spacer(1, 7)]))
            i += 2
            continue
        out.append(KeepTogether(a + [Spacer(1, 7)]))
        i += 1
    return out


def dive_text(n, blank=False):
    lines = []
    for k in range(n, -1, -1):
        pad = "  " * (n - k)
        if blank:
            lines.append("%sAUX(%d)   ______" % (pad, k))
        elif k == 0:
            lines.append("%sAUX(0)   MISS -> n == 0, so q = 0; r[0] = 0; "
                         "return 0" % pad)
        else:
            lines.append("%sAUX(%d)   MISS -> r[%d] = -inf, so take i = 1 and "
                         "call AUX(%d)" % (pad, k, k, k - 1))
    return "\n".join(lines)


def memo_counts(n):
    total = 1 + n * (n + 1) // 2
    return total, n + 1, total - (n + 1)


# ------------------------------------------------------------- problem sets

WORKED_BU = [
    ("Worked Example B-1", [2, 5, 7, 8],
     "Small and quick. Watch j = 3, where all three columns produce the same "
     "total, so the tie rule decides s[3]."),
    ("Worked Example B-2", [1, 4, 8, 9, 10, 17],
     "Six lengths, and the answer at the end is 'do not cut at all'. Ties "
     "appear in almost every block, so it exercises the tie rule for s."),
]

WORKED_TD = [
    ("Worked Example T-1", [2, 5, 9, 10, 12],
     "Follow the dive all the way to AUX(0) before doing any arithmetic."),
    ("Worked Example T-2", [2, 6, 7, 10, 13, 14],
     "Larger frame count. Every call after the dive is a memo hit."),
]

PRACTICE_BU = [
    ("P1", [2, 5, 6, 9]),
    ("P2", [2, 3, 7, 8, 9]),
    ("P3", [3, 4, 6, 10, 12]),
    ("P4", [1, 5, 8, 9, 10, 17]),
    ("P5", [1, 6, 7, 12, 15, 18, 21]),
]

PRACTICE_TD = [
    ("P6", [1, 5, 8, 9]),
    ("P7", [1, 4, 7, 9, 12]),
    ("P8", [2, 4, 9, 11, 13]),
    ("P9", [3, 7, 8, 11, 13, 20]),
    ("P10", [1, 3, 8, 10, 12, 17, 18]),
]

PSEUDO_BU = """BOTTOM-UP-CUT-ROD(p, n)          EXTENDED-BOTTOM-UP-CUT-ROD(p, n)
  let r[0..n] be a new array       1  let r[0..n] and s[0..n] be new arrays
  r[0] = 0                         2  r[0] = 0
  for j = 1 to n                   3  for j = 1 to n
      q = -inf                     4      q = -inf
      for i = 1 to j               5      for i = 1 to j
          q = max(q,p[i]+r[j-i])   6          if q < p[i] + r[j-i]
      r[j] = q                     7              q = p[i] + r[j-i]
  return r[n]                      8              s[j] = i
                                   9      r[j] = q
                                  10  return r and s"""

PSEUDO_TD = """MEMOIZED-CUT-ROD(p, n)             MEMOIZED-CUT-ROD-AUX(p, n, r)
 1  let r[0..n] be a new array      1  if r[n] >= 0
 2  for i = 0 to n                  2      return r[n]
 3      r[i] = -inf                 3  if n == 0
 4  return MEMOIZED-CUT-ROD-AUX(    4      q = 0
        p, n, r)                    5  else q = -inf
                                    6      for i = 1 to n
PRINT-CUT-ROD-SOLUTION(p, n)        7          q = max(q, p[i] +
 1  (r,s) = EXTENDED-BOTTOM-UP-             MEMOIZED-CUT-ROD-AUX(p,n-i,r))
        CUT-ROD(p, n)               8  r[n] = q
 2  while n > 0                     9  return q
 3      print s[n]
 4      n = n - s[n]"""


# ------------------------------------------------------------ document body

def method_section():
    st = []
    st.append(Paragraph("Part 1 &nbsp;|&nbsp; The two algorithms", H1))
    st.append(Paragraph(
        "These are the versions from the course slides. Everything in this "
        "workbook uses this exact indexing: <font face='Courier'>p[i]</font> "
        "is the price of a piece of length <i>i</i>, there is no "
        "<font face='Courier'>p[0]</font>, and "
        "<font face='Courier'>r[j]</font> is the best revenue obtainable "
        "from a rod of length <i>j</i>.", BODY))
    st.append(Spacer(1, 4))
    st.append(code_box(PSEUDO_BU, size=7.7))
    st.append(Spacer(1, 6))
    st.append(code_box(PSEUDO_TD, size=7.7))
    st.append(Spacer(1, 6))
    st.append(callout("Facts worth having cold", [
        "&bull; A rod of length <i>n</i> has <i>n</i>-1 possible cut "
        "positions, each cut or not, so there are 2<super>n-1</super> ways "
        "to cut it.",
        "&bull; Plain recursive CUT-ROD explores all of them: "
        "O(2<super>n</super>) time.",
        "&bull; Both DP versions: O(n<super>2</super>) time, O(n) space. "
        "Bottom-up has the smaller constant factor because it makes no "
        "recursive calls.",
        "&bull; The O(n<super>2</super>) bound for the top-down version comes "
        "from aggregate analysis: frame <i>k</i> runs its loop <i>k</i> "
        "times, and 1 + 2 + ... + n is n(n+1)/2.",
        "&bull; Greedy on price-per-unit-length is wrong. With p = 1, 5, 8, 9 "
        "and n = 4, length 3 has the best density (8/3), and greedy yields "
        "8 + 1 = 9, but the optimum is 5 + 5 = 10.",
    ]))
    st.append(PageBreak())

    # ---- Method A
    st.append(Paragraph("Part 2 &nbsp;|&nbsp; Method A: running BOTTOM-UP-"
                        "CUT-ROD on paper", H1))
    st.append(Paragraph(
        "The whole difficulty of this algorithm by hand is that "
        "<font face='Courier'>i</font> counts up while "
        "<font face='Courier'>j - i</font> counts down, so you are reading "
        "one array forward and another backward at the same time. The method "
        "below removes that problem by writing the two directions on separate "
        "rows and never mixing them.", BODY))

    st.append(Paragraph("Setup", H2))
    for txt in [
        "<b>A0.</b> Copy the price table. Confirm it has exactly <i>n</i> "
        "entries and that the leftmost is p[1], not p[0].",
        "<b>A1.</b> Draw the <b>r-strip</b>: a single row of boxes labelled "
        "0, 1, 2, ..., <i>n</i>. Write 0 in box 0. Leave the rest empty. "
        "This strip is the only place r values live.",
        "<b>A2.</b> Rule <i>n</i> <b>j-blocks</b> below it, one per "
        "j = 1..n. Block <i>j</i> has exactly <i>j</i> data columns and six "
        "labelled rows: i, p[i], j-i, r[j-i], p[i]+r[j-i], q after.",
    ]:
        st.append(Paragraph(txt, STEP))

    st.append(Paragraph("Fill each block by rows, never by columns", H2))
    for txt in [
        "<b>A3.</b> Row <b>i</b>: write 1, 2, ..., j. Then count them. There "
        "must be exactly <i>j</i>. (The inner loop stops at <i>j</i>, not at "
        "<i>n</i>. This is the single most common error.)",
        "<b>A4.</b> Row <b>p[i]</b>: copy the first <i>j</i> prices straight "
        "off the table, left to right. No arithmetic, no thinking.",
        "<b>A5.</b> Row <b>j-i</b>: write j-1, j-2, ..., 1, 0. It always ends "
        "in 0. Writing the index before the value is what stops the "
        "reversal error.",
        "<b>A6.</b> Row <b>r[j-i]</b>: for each index you just wrote, copy "
        "the value out of that box of the r-strip. You are reading the strip "
        "<b>backwards</b>, from box j-1 down to box 0. The last entry of this "
        "row is always 0.",
        "<b>A7.</b> Row <b>p[i]+r[j-i]</b>: add the two rows above, column by "
        "column. This is pure addition with no decisions in it, so do the "
        "whole row before you compare anything.",
        "<b>A8.</b> Row <b>q after</b>: now scan the sum row left to right "
        "carrying a running maximum that starts at -inf. Write each step in "
        "the lecture's form, <font face='Courier'>i = 1 -&gt; q = "
        "max(-inf, __)</font>. q never decreases as you move right.",
        "<b>A9.</b> r[j] is the last q in the row. <b>Immediately</b> go up "
        "and write it into box <i>j</i> of the r-strip. Do not start block "
        "j+1 until that box is filled.",
        "<b>A10.</b> If the problem asks for the cuts: s[j] is the "
        "<b>leftmost</b> column whose sum equals r[j]. The slide's update "
        "test is a strict <font face='Courier'>if q &lt; ...</font>, so a "
        "tie does not overwrite and the smaller <i>i</i> wins.",
    ]:
        st.append(Paragraph(txt, STEP))

    st.append(Paragraph("Check before moving on", H2))
    st.append(callout("Five checks, all fast", [
        "<b>V1 &nbsp;Width.</b> Block <i>j</i> has exactly <i>j</i> columns.",
        "<b>V2 &nbsp;Right edge.</b> The last column is always p[j] + r[0] = "
        "p[j]. If the sum there is not exactly p[j], you misread the table.",
        "<b>V3 &nbsp;Left edge.</b> The first column is always p[1] + r[j-1].",
        "<b>V4 &nbsp;Growth.</b> r[j] must be at least r[j-1] + p[1] and at "
        "least p[j], since both are achievable. If r[j] is below either, you "
        "have an arithmetic error.",
        "<b>V5 &nbsp;Recycling.</b> Block <i>j</i>'s p-row is block j-1's "
        "p-row with p[j] <i>appended</i> on the right; block <i>j</i>'s "
        "r-row is block j-1's r-row with r[j-1] <i>prepended</i> on the "
        "left. The two rows grow from opposite ends. If a block does not "
        "line up with the one above it that way, one of them is wrong.",
    ]))
    st.append(Spacer(1, 6))
    st.append(Paragraph(
        "<b>Reading off the answer.</b> The revenue is r[n], the last box of "
        "the strip. For the cuts, start at n, print s[n], subtract s[n], and "
        "repeat until you reach 0. Add up the prices of the pieces you "
        "printed; the total must equal r[n]. That is a complete "
        "self-check on the s array.", BODY))

    st.append(PageBreak())

    # ---- Method B
    st.append(Paragraph("Part 3 &nbsp;|&nbsp; Method B: running MEMOIZED-CUT-"
                        "ROD on paper", H1))
    st.append(Paragraph(
        "One structural fact makes this tractable by hand. The loop starts at "
        "<font face='Courier'>i = 1</font> and recurses on "
        "<font face='Courier'>n - i</font>, so the very first thing any frame "
        "does is call the frame one smaller. The algorithm therefore dives "
        "straight down n, n-1, n-2, ..., 0 before it computes a single sum. "
        "It reaches the base case, unwinds, and from that moment on "
        "<b>every</b> recursive call finds its answer already in "
        "<font face='Courier'>r</font>. So a hand trace has exactly two "
        "phases, and all the arithmetic is in the second one.", BODY))

    st.append(Paragraph("Phase 0 &mdash; Setup", H2))
    for txt in [
        "<b>B0.</b> Copy the price table.",
        "<b>B1.</b> Draw the <b>memo strip</b> r[0..n] and write "
        "<font face='Courier'>-inf</font> in <i>every</i> box, box 0 "
        "included. Lines 2-3 of MEMOIZED-CUT-ROD initialise all of them to "
        "-inf; r[0] does not become 0 until the base case actually runs.",
        "<b>B2.</b> Draw a small tally box with three counters: calls, "
        "misses, hits.",
    ]:
        st.append(Paragraph(txt, STEP))

    st.append(Paragraph("Phase 1 &mdash; The dive (no arithmetic at all)", H2))
    for txt in [
        "<b>B3.</b> Write the descending chain, one line per frame, each "
        "indented one step further: AUX(n), AUX(n-1), ..., AUX(1), AUX(0). "
        "Mark every one <b>MISS</b>.",
        "<b>B4.</b> At AUX(0), line 1 fails (r[0] is still -inf), line 3 "
        "succeeds, so q = 0, line 8 sets r[0] = 0, and it returns 0. Write "
        "the 0 into box 0 of the memo strip now.",
        "<b>B5.</b> Those <i>n</i>+1 misses are the only misses in the entire "
        "run. Every remaining call is a hit.",
    ]:
        st.append(Paragraph(txt, STEP))

    st.append(Paragraph("Phase 2 &mdash; The unwind (all the arithmetic)", H2))
    for txt in [
        "<b>B6.</b> Resolve the frames <b>smallest first</b>: k = 1, then 2, "
        "then 3, up to n. Frame 0 is already finished.",
        "<b>B7.</b> Frame <i>k</i> gets a five-column ledger with exactly "
        "<i>k</i> rows, one per i = 1..k: "
        "<font face='Courier'>i | call | returns | p[i]+ret | q after</font>. "
        "Note the loop bound here is the frame's own <i>n</i>, which is "
        "<i>k</i>.",
        "<b>B8.</b> In the <b>call</b> column write AUX(k-i). In "
        "<b>returns</b> write the value read straight out of box k-i of the "
        "memo strip. Tag row i = 1 <b>dive</b>, because that is the call the "
        "frame already made on the way down; tag every other row <b>hit</b>. "
        "If a box you need still says -inf, stop: you are resolving frames "
        "out of order.",
        "<b>B9.</b> Fill <b>p[i]+ret</b> for the whole column first, then "
        "sweep <b>q after</b> downward as a running maximum starting at "
        "-inf. Same discipline as Method A.",
        "<b>B10.</b> Line 8: r[k] = q. Write it into box <i>k</i> of the memo "
        "strip before you begin frame k+1.",
    ]:
        st.append(Paragraph(txt, STEP))

    st.append(Paragraph("Check before moving on", H2))
    st.append(callout("Checks and the counting questions", [
        "<b>W1 &nbsp;The cross-check that matters.</b> Frame <i>k</i>'s "
        "ledger holds exactly the same numbers, in the same order, as "
        "bottom-up block <i>j</i> = <i>k</i>. The two algorithms differ only "
        "in bookkeeping, never in arithmetic. If your two traces disagree "
        "anywhere, one of them has a slip.",
        "<b>W2 &nbsp;Height.</b> Frame <i>k</i>'s ledger has exactly "
        "<i>k</i> rows, and exactly one of them &mdash; the first &mdash; is "
        "a dive call. Every other row is a hit. If you have written a second "
        "miss anywhere in a frame, something is wrong.",
        "<b>W3 &nbsp;Misses.</b> = n + 1, one per distinct subproblem "
        "(lengths 0 through n).",
        "<b>W4 &nbsp;Total invocations.</b> = 1 + n(n+1)/2. The 1 is the "
        "top-level call from MEMOIZED-CUT-ROD; frame <i>k</i> makes <i>k</i> "
        "recursive calls, and those sum to n(n+1)/2.",
        "<b>W5 &nbsp;Hits.</b> = total - misses = n(n-1)/2.",
        "<b>W6 &nbsp;Max stack depth.</b> = n + 1 frames, reached at the "
        "bottom of the dive.",
    ]))
    st.append(Spacer(1, 8))
    st.append(callout("Eight mistakes to rule out by habit", [
        "1. Reading the r-strip forward instead of backward in the r[j-i] "
        "row. Write the indices first; they are your guard rail.",
        "2. Letting the bottom-up inner loop run to <i>n</i> instead of to "
        "<i>j</i>.",
        "3. Forgetting to reset q = -inf at the top of each new j or each "
        "new frame.",
        "4. Computing r[j] correctly and then not writing it into the strip "
        "before starting the next block.",
        "5. Assuming r[0] = 0 at initialisation in the top-down version. It "
        "is -inf until the base case runs, which is why AUX(0) is a miss the "
        "first time.",
        "6. Treating the top-down loop as if it stops at some fixed n. In "
        "frame <i>k</i> it runs i = 1..k.",
        "7. Off-by-one on prices: p[i] is the price of length <i>i</i>, and "
        "p[0] does not exist. r[0] = 0 is a revenue, not a price.",
        "8. Overwriting s[j] on a tie. The test is strict, so the smallest "
        "<i>i</i> that achieves the maximum is the one kept.",
    ], tint="#fbf7f2"))
    return st


def worked_bottom_up(title, p, blurb):
    n = len(p)
    r, s, blocks = bottom_up(p, n)
    st = [Paragraph(title, H1), Paragraph(blurb, NOTE), Spacer(1, 6),
          price_table(p), Spacer(1, 8),
          Paragraph("Final r-strip (fill yours in one box at a time, "
                    "left to right):", BODY),
          Spacer(1, 3), r_strip(n, r), Spacer(1, 10)]
    st.extend(layout_blocks([(b["j"], b["rows"], b["r_j"], b["s_j"])
                             for b in blocks]))
    cuts = cut_list(s, n)
    total = sum(p[c - 1] for c in cuts)
    st.append(Spacer(1, 2))
    st.append(CondPageBreak(110))
    st.append(callout("Answer", [
        "<b>r[%d] = %d</b>" % (n, r[n]),
        "s = [%s] for j = 1..%d" % (", ".join(str(x) for x in s[1:]), n),
        "PRINT-CUT-ROD-SOLUTION walks %s, giving pieces %s."
        % (" -> ".join(["n = %d" % n] +
                       ["n = %d" % v for v in _walk(s, n)]),
           " + ".join(str(c) for c in cuts)),
        "Check: %s = %d, which matches r[%d]."
        % (" + ".join("p[%d]=%d" % (c, p[c - 1]) for c in cuts), total, n),
    ]))
    st.append(Spacer(1, 8))
    st.append(CondPageBreak(90))
    st.append(Paragraph("The same trace in the running form used on the "
                        "lecture slides:", BODY))
    st.append(Spacer(1, 3))
    st.append(code_box(lecture_trace(blocks), size=7.9))
    st.append(PageBreak())
    return st


def _walk(s, n):
    out = []
    while n > 0:
        n -= s[n]
        out.append(n)
    return out


def worked_top_down(title, p, blurb):
    n = len(p)
    m = MemoTrace(p, n)
    total, misses, hits = memo_counts(n)
    st = [Paragraph(title, H1), Paragraph(blurb, NOTE), Spacer(1, 6),
          price_table(p), Spacer(1, 8),
          Paragraph("<b>Phase 0.</b> Memo strip after lines 2-3 of "
                    "MEMOIZED-CUT-ROD &mdash; every box, including box 0, "
                    "starts at -inf:", BODY), Spacer(1, 3),
          r_strip(n, ["-inf"] * (n + 1)), Spacer(1, 9),
          Paragraph("<b>Phase 1 &mdash; the dive.</b> Only i = 1 is reached "
                    "in each frame on the way down, so no sums are computed "
                    "yet:", BODY), Spacer(1, 3),
          code_box(dive_text(n), size=7.6), Spacer(1, 9),
          Paragraph("<b>Phase 2 &mdash; the unwind.</b> Frames finish "
                    "smallest first. In each frame the i = 1 row is the call "
                    "the frame already made on the way down; every other row "
                    "is a memo hit:", BODY),
          Spacer(1, 5)]
    st.extend(layout_frames([
        {"k": f["n"], "rows": f["rows"], "r_k": f["r_n"],
         "snapshot": f["r_snapshot"]}
        for f in m.unwind_order() if f["n"] != 0]))
    st.append(Spacer(1, 4))
    st.append(CondPageBreak(110))
    st.append(callout("Answer", [
        "<b>MEMOIZED-CUT-ROD(p, %d) returns %d</b>, the same value "
        "BOTTOM-UP-CUT-ROD gives." % (n, m.result),
        "Final memo: r = [%s]" % ", ".join(fmt(v) for v in m.r),
        "Invocations of MEMOIZED-CUT-ROD-AUX: <b>%d</b> = 1 + %d(%d+1)/2. "
        "Misses <b>%d</b> = n+1. Hits <b>%d</b> = n(n-1)/2."
        % (total, n, n, misses, hits),
        "Maximum stack depth: %d frames." % (n + 1),
    ]))
    st.append(PageBreak())
    return st


def _memo_snapshot(vals):
    txt = "memo now: r = [%s]" % ", ".join(fmt(v) for v in vals)
    return Paragraph("<font face='Courier' size='8'>%s</font>" % txt,
                     ParagraphStyle("ms", parent=MONO, fontSize=8,
                                    leftIndent=6, spaceAfter=9,
                                    textColor=colors.HexColor("#555555")))


# ---------------------------------------------------------------- worksheets

def worksheet_bottom_up(tag, p):
    n = len(p)
    st = [Paragraph("%s &nbsp;&mdash;&nbsp; BOTTOM-UP-CUT-ROD, n = %d"
                    % (tag, n), H1),
          Paragraph("Run BOTTOM-UP-CUT-ROD (extended, so track s as well). "
                    "Fill the blocks by rows, in the order i, p[i], j-i, "
                    "r[j-i], sum, q. Write each r[j] into the strip before "
                    "starting the next block.", NOTE),
          Spacer(1, 6), price_table(p), Spacer(1, 9),
          Paragraph("<b>r-strip</b>", BODY), Spacer(1, 3),
          r_strip(n), Spacer(1, 10)]
    st.extend(layout_blocks([(j, None, None, None)
                             for j in range(1, n + 1)]))
    st.append(Spacer(1, 4))
    st.append(callout("Report", [
        "r[%d] = __________ &nbsp;&nbsp; s[1..%d] = "
        "________________________________" % (n, n),
        "Pieces (PRINT-CUT-ROD-SOLUTION) = ____________________ &nbsp;&nbsp; "
        "their prices sum to __________ (must equal r[%d])" % n,
    ]))
    st.append(PageBreak())
    return st


def worksheet_top_down(tag, p):
    n = len(p)
    st = [Paragraph("%s &nbsp;&mdash;&nbsp; MEMOIZED-CUT-ROD, n = %d"
                    % (tag, n), H1),
          Paragraph("Run MEMOIZED-CUT-ROD. Do the dive first with no "
                    "arithmetic, then unwind the frames smallest first. Tag "
                    "every call hit or miss as you go.", NOTE),
          Spacer(1, 6), price_table(p), Spacer(1, 9),
          Paragraph("<b>Memo strip</b> (start every box at -inf)", BODY),
          Spacer(1, 3), r_strip(n, [""] * (n + 1)), Spacer(1, 9),
          Paragraph("<b>Phase 1 &mdash; the dive</b>", BODY), Spacer(1, 3),
          code_box(dive_text(n, blank=True), size=7.8), Spacer(1, 9),
          Paragraph("<b>Phase 2 &mdash; the unwind</b>", BODY), Spacer(1, 5)]
    st.extend(layout_frames([{"k": k} for k in range(1, n + 1)]))
    st.append(Spacer(1, 4))
    st.append(callout("Report", [
        "Returns __________ &nbsp;&nbsp; final memo r[0..%d] = "
        "________________________________" % n,
        "AUX invocations __________ &nbsp; misses __________ &nbsp; "
        "hits __________ &nbsp; max stack depth __________",
    ]))
    st.append(PageBreak())
    return st


# ------------------------------------------------------------- answer key

def key_bottom_up(tag, p):
    n = len(p)
    r, s, blocks = bottom_up(p, n)
    cuts = cut_list(s, n)
    st = [Paragraph("%s &nbsp;&mdash;&nbsp; BOTTOM-UP-CUT-ROD, n = %d"
                    % (tag, n), H1),
          price_table(p), Spacer(1, 8), r_strip(n, r), Spacer(1, 10)]
    st.extend(layout_blocks([(b["j"], b["rows"], b["r_j"], b["s_j"])
                             for b in blocks]))
    st.append(Spacer(1, 2))
    st.append(callout("Answers", [
        "<b>r[%d] = %d</b>" % (n, r[n]),
        "r[0..%d] = [%s]" % (n, ", ".join(str(v) for v in r)),
        "s[1..%d] = [%s]" % (n, ", ".join(str(v) for v in s[1:])),
        "Pieces: %s &nbsp;&rarr;&nbsp; %s = %d"
        % (" + ".join(str(c) for c in cuts),
           " + ".join("p[%d]=%d" % (c, p[c - 1]) for c in cuts),
           sum(p[c - 1] for c in cuts)),
    ]))
    st.append(Spacer(1, 8))
    st.append(code_box(lecture_trace(blocks), size=7.6))
    st.append(PageBreak())
    return st


def key_top_down(tag, p):
    n = len(p)
    m = MemoTrace(p, n)
    total, misses, hits = memo_counts(n)
    st = [Paragraph("%s &nbsp;&mdash;&nbsp; MEMOIZED-CUT-ROD, n = %d"
                    % (tag, n), H1),
          price_table(p), Spacer(1, 8),
          Paragraph("<b>Dive</b>", BODY), Spacer(1, 3),
          code_box(dive_text(n), size=7.5), Spacer(1, 9),
          Paragraph("<b>Unwind</b>", BODY), Spacer(1, 5)]
    st.extend(layout_frames([
        {"k": f["n"], "rows": f["rows"], "r_k": f["r_n"],
         "snapshot": f["r_snapshot"]}
        for f in m.unwind_order() if f["n"] != 0]))
    st.append(Spacer(1, 2))
    st.append(callout("Answers", [
        "<b>Returns %d.</b>  Final memo r = [%s]"
        % (m.result, ", ".join(fmt(v) for v in m.r)),
        "Invocations <b>%d</b> &nbsp; misses <b>%d</b> &nbsp; hits <b>%d</b> "
        "&nbsp; max stack depth <b>%d</b>" % (total, misses, hits, n + 1),
        "Cross-check: these ledgers match the bottom-up blocks for the same "
        "price table, row for row.",
    ]))
    st.append(PageBreak())
    return st


def summary_table():
    rows = [["Problem", "Algorithm", "n", "prices p[1..n]", "r[n]",
             "s[1..n]", "pieces", "calls/miss/hit"]]
    for tag, p in PRACTICE_BU:
        n = len(p)
        r, s, _ = bottom_up(p, n)
        rows.append([tag, "bottom-up", str(n),
                     ",".join(map(str, p)), str(r[n]),
                     ",".join(map(str, s[1:])),
                     "+".join(map(str, cut_list(s, n))), "-"])
    for tag, p in PRACTICE_TD:
        n = len(p)
        r, s, _ = bottom_up(p, n)
        t, ms, h = memo_counts(n)
        rows.append([tag, "top-down", str(n),
                     ",".join(map(str, p)), str(r[n]),
                     ",".join(map(str, s[1:])),
                     "+".join(map(str, cut_list(s, n))),
                     "%d/%d/%d" % (t, ms, h)])
    t = Table(rows, colWidths=[40, 56, 20, 112, 34, 76, 64, 80],
              rowHeights=[16] + [15] * (len(rows) - 1))
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Courier", 7.6),
        ("FONT", (0, 0), (-1, 0), "Courier-Bold", 7.6),
        ("FONT", (4, 1), (4, -1), "Courier-Bold", 8),
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("BACKGROUND", (0, 0), (-1, 0), FILLHDR),
        ("BACKGROUND", (0, 6), (-1, -1), colors.HexColor("#fafafa")),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("ALIGN", (3, 1), (3, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


# ------------------------------------------------------------------- build

def build_workbook(path):
    st = [Paragraph("Rod Cutting by Hand", TITLE),
          Paragraph("A drill book for BOTTOM-UP-CUT-ROD and "
                    "MEMOIZED-CUT-ROD &mdash; CMP SCI 5130, CLRS 15.1",
                    SUB)]
    st.append(Paragraph(
        "This workbook is built around one idea: the arithmetic in these two "
        "algorithms is trivial, and essentially every mistake made under quiz "
        "conditions is a bookkeeping mistake. So the method below fixes where "
        "each number is written down before any number is computed, and gives "
        "you cheap checks that catch a slip within a few seconds of making "
        "it.", BODY))
    st.append(Spacer(1, 4))
    st.append(Paragraph(
        "Parts 2 and 3 are the procedures. Part 4 works four examples all the "
        "way through. Part 5 has ten problems with the grids pre-drawn: five "
        "bottom-up, five top-down. Answers are in the companion key, so mark "
        "your own work rather than checking as you go.", BODY))
    st.extend(rule())
    st.extend(method_section())

    st.append(Paragraph("Part 4 &nbsp;|&nbsp; Worked examples", H1))
    st.append(Paragraph(
        "Two of each. Read the first of each pair with the procedure beside "
        "you, then cover the answers and redo the second one yourself before "
        "starting Part 5.", BODY))
    st.append(PageBreak())
    for title, p, blurb in WORKED_BU:
        st.extend(worked_bottom_up(title, p, blurb))
    for title, p, blurb in WORKED_TD:
        st.extend(worked_top_down(title, p, blurb))

    st.append(Paragraph("Part 5 &nbsp;|&nbsp; Practice problems", H1))
    st.append(Paragraph(
        "P1 through P5 are bottom-up, P6 through P10 are top-down. Each is "
        "on its own page with the grids already ruled. Time yourself: at the "
        "sizes here, a clean bottom-up run should take four or five minutes, "
        "a top-down run slightly longer because of the dive.", BODY))
    st.append(Spacer(1, 6))
    st.append(Paragraph(
        "P6 uses the same price table as the lecture slides, where "
        "bottom-up gives r[4] = 10. Top-down must return the same 10. If it "
        "does not, the error is in your bookkeeping, not in the problem.",
        NOTE))
    st.append(PageBreak())
    for tag, p in PRACTICE_BU:
        st.extend(worksheet_bottom_up(tag, p))
    for tag, p in PRACTICE_TD:
        st.extend(worksheet_top_down(tag, p))

    Doc(path, {"title": "Rod Cutting by Hand - Practice Workbook",
               "left": "Rod cutting by hand - practice workbook"}).build(st)


def build_key(path):
    st = [Paragraph("Rod Cutting by Hand &mdash; Answer Key", TITLE),
          Paragraph("Full traces for P1 through P10", SUB)]
    st.append(Paragraph(
        "Every value here was produced by executing the pseudocode from the "
        "course slides, not written by hand. Mark your work block by block "
        "rather than only comparing the final r[n]: a wrong r[n] tells you "
        "nothing about where the slip was, and the first block that "
        "disagrees usually explains all the ones after it.", BODY))
    st.append(Spacer(1, 8))
    st.append(Paragraph("Answers at a glance", H2))
    st.append(summary_table())
    st.append(Spacer(1, 8))
    st.append(Paragraph(
        "The s column and pieces column are shown for the top-down problems "
        "too, even though MEMOIZED-CUT-ROD does not compute s. They come "
        "from running the extended bottom-up version on the same price table "
        "&mdash; useful if you want to reuse those tables for cut-recovery "
        "practice.", NOTE))
    st.append(PageBreak())
    for tag, p in PRACTICE_BU:
        st.extend(key_bottom_up(tag, p))
    for tag, p in PRACTICE_TD:
        st.extend(key_top_down(tag, p))
    Doc(path, {"title": "Rod Cutting by Hand - Answer Key",
               "left": "Rod cutting by hand - answer key"}).build(st)


if __name__ == "__main__":
    build_workbook("/home/claude/rod-cutting-practice-workbook.pdf")
    build_key("/home/claude/rod-cutting-answer-key.pdf")
    print("built")
