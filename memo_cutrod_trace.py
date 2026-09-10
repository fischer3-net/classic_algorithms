#!/usr/bin/env python3
"""
memo_cutrod_trace.py -- walk MEMOIZED-CUT-ROD by hand, on screen.

Generates a random price table for a rod of length n and traces
MEMOIZED-CUT-ROD exactly as you would run it on paper: the dive first,
then the frames unwound smallest first, with each frame's ledger table
filled in one row per iteration of the inner loop.

    python3 memo_cutrod_trace.py 5
    python3 memo_cutrod_trace.py 6 --step          # redraw after every row
    python3 memo_cutrod_trace.py 4 --seed 17       # reproducible table
    python3 memo_cutrod_trace.py 5 --prices 1,5,8,9,10

Pseudocode traced (CLRS 15.1, as given on the course slides):

    MEMOIZED-CUT-ROD(p, n)            MEMOIZED-CUT-ROD-AUX(p, n, r)
     1  let r[0..n] be a new array     1  if r[n] >= 0
     2  for i = 0 to n                 2      return r[n]
     3      r[i] = -inf                3  if n == 0
     4  return MEMOIZED-CUT-ROD-AUX(   4      q = 0
            p, n, r)                   5  else q = -inf
                                       6      for i = 1 to n
                                       7          q = max(q, p[i] +
                                                  MEMOIZED-CUT-ROD-AUX(p,n-i,r))
                                       8  r[n] = q
                                       9  return q

Standard library only.
"""

import argparse
import random
import sys

NEG = float("-inf")


def fmt(v):
    return "-inf" if v == NEG else str(v)


# ---------------------------------------------------------------- rendering

def rule(widths):
    return "+" + "+".join("-" * (w + 2) for w in widths) + "+"


def row(cells, widths, align):
    out = []
    for cell, w, a in zip(cells, widths, align):
        out.append(" " + (cell.rjust(w) if a == "r" else
                          cell.center(w) if a == "c" else cell.ljust(w)) + " ")
    return "|" + "|".join(out) + "|"


def table(header, rows, align, indent=2):
    """Render a fixed-width ASCII table; blank rows print as empty cells."""
    widths = [len(h) for h in header]
    for r in rows:
        for k, cell in enumerate(r):
            widths[k] = max(widths[k], len(cell))
    pad = " " * indent
    lines = [pad + rule(widths),
             pad + row(header, widths, ["c"] * len(header)),
             pad + rule(widths)]
    for r in rows:
        lines.append(pad + row(r, widths, align))
    lines.append(pad + rule(widths))
    return "\n".join(lines)


LEDGER_HEAD = ["i", "call", "returns", "p[i] + ret", "q after"]
LEDGER_ALIGN = ["r", "l", "l", "r", "r"]


def ledger(k, rows, r_k=None):
    body = [[str(rw["i"]), "AUX(%d)" % rw["sub_n"],
             "%-4s %s" % (rw["tag"], fmt(rw["sub_val"])),
             str(rw["total"]), fmt(rw["q_after"])] for rw in rows]
    out = [table(LEDGER_HEAD, body, LEDGER_ALIGN)]
    if r_k is not None:
        out.append("  line 8:  r[%d] = %s" % (k, fmt(r_k)))
    return "\n".join(out)


def memo_line(r, label="memo now"):
    return "  %s: r = [%s]" % (label, ", ".join(fmt(v) for v in r))


def price_table(p):
    n = len(p)
    head = ["length i"] + [str(i) for i in range(1, n + 1)]
    body = [["price p[i]"] + [str(v) for v in p]]
    return table(head, body, ["l"] + ["r"] * n)


def banner(text, ch="="):
    return "\n%s\n%s" % (text, ch * len(text))


# ------------------------------------------------------------------- tracer

class Tracer:
    """Runs MEMOIZED-CUT-ROD, printing the trace as it goes."""

    def __init__(self, p, n, step=False, out=sys.stdout):
        self.p = p
        self.n = n
        self.step = step
        self.out = out
        self.r = [NEG] * (n + 1)        # lines 2-3 of MEMOIZED-CUT-ROD
        self.frames = {}                # n -> list of ledger rows
        self.dive = []
        self.calls = 0
        self.hits = 0
        self.misses = 0

    def say(self, *lines):
        for ln in lines:
            print(ln, file=self.out)

    def pause(self):
        if self.step:
            try:
                input("  [enter to continue] ")
            except EOFError:
                print()
                self.step = False

    # -- the algorithm itself, instrumented ------------------------------

    def aux(self, n, depth=0):
        self.calls += 1
        if self.r[n] >= 0:                                      # line 1
            self.hits += 1
            return self.r[n], True                              # line 2
        self.misses += 1
        self.dive.append((depth, n))
        rows = []
        self.frames[n] = rows
        self.drawn = getattr(self, "drawn", set())
        if n == 0:                                              # line 3
            q = 0                                               # line 4
        else:
            q = NEG                                             # line 5
            for i in range(1, n + 1):                           # line 6
                sub, was_hit = self.aux(n - i, depth + 1)       # line 7
                total = self.p[i - 1] + sub
                q = max(q, total)
                rows.append({"i": i, "sub_n": n - i, "sub_val": sub,
                             "tag": "hit" if was_hit else "dive",
                             "total": total, "q_after": q})
                if i == 1:
                    self.open_frame(n)
                self.redraw(n, rows)
        self.r[n] = q                                           # line 8
        self.close_frame(n, q)
        return q, False                                         # line 9

    # -- presentation hooks ---------------------------------------------

    def open_frame(self, n):
        self.say("", "Frame n = %d   (loop runs i = 1..%d)" % (n, n))

    def redraw(self, n, rows):
        """Show the ledger as it stands after this iteration of the i loop."""
        if self.step:
            self.say(ledger(n, rows))
            self.drawn.add(n)
            self.pause()

    def close_frame(self, n, q):
        if n == 0:
            return
        if n in self.drawn:
            self.say("  line 8:  r[%d] = %s" % (n, fmt(q)))
        else:
            self.say(ledger(n, self.frames[n], q))
        self.say(memo_line(self.r))


# ------------------------------------------------------------- cross-checks

def bottom_up(p, n):
    r = [0] + [NEG] * n
    s = [0] * (n + 1)
    for j in range(1, n + 1):
        q = NEG
        for i in range(1, j + 1):
            if q < p[i - 1] + r[j - i]:
                q = p[i - 1] + r[j - i]
                s[j] = i
        r[j] = q
    return r, s


def cuts(s, n):
    out = []
    while n > 0:
        out.append(s[n])
        n -= s[n]
    return out


# -------------------------------------------------------------------- input

def _draw_prices(n, rng):
    """Non-decreasing, but with per-length bargains and premiums so that
    the optimum is rarely just 'all unit pieces' or 'do not cut'."""
    base = rng.randint(2, 5)
    p, prev = [], 0
    for i in range(1, n + 1):
        v = max(1, int(round(i * base * rng.uniform(0.70, 1.30))))
        prev = max(prev, v)
        p.append(prev)
    return p


def _is_interesting(p, n):
    """Prefer a table whose optimal solution mixes at least two piece
    lengths -- those exercise the max comparison properly."""
    _, s = bottom_up(p, n)
    pieces = cuts(s, n)
    return len(set(pieces)) > 1


def random_prices(n, rng, tries=300):
    p = _draw_prices(n, rng)
    if n < 3:
        return p
    for _ in range(tries):
        if _is_interesting(p, n):
            return p
        p = _draw_prices(n, rng)
    return p


def parse_args(argv):
    ap = argparse.ArgumentParser(
        description="Trace MEMOIZED-CUT-ROD on a random price table.")
    ap.add_argument("n", type=int, help="rod length (1..12 is practical)")
    ap.add_argument("--seed", type=int, default=None,
                    help="seed the price-table generator for a repeatable run")
    ap.add_argument("--prices", default=None,
                    help="use this table instead, e.g. --prices 1,5,8,9")
    ap.add_argument("--step", action="store_true",
                    help="redraw the frame table after every loop iteration "
                         "and wait for enter")
    a = ap.parse_args(argv)
    if a.n < 1:
        ap.error("n must be at least 1")
    if a.prices:
        try:
            p = [int(x) for x in a.prices.replace(" ", "").split(",") if x]
        except ValueError:
            ap.error("--prices must be a comma-separated list of integers")
        if len(p) != a.n:
            ap.error("--prices has %d entries but n = %d" % (len(p), a.n))
        a.price_list = p
    else:
        a.price_list = random_prices(a.n, random.Random(a.seed))
    return a


# --------------------------------------------------------------------- main

def main(argv=None):
    a = parse_args(argv if argv is not None else sys.argv[1:])
    n, p = a.n, a.price_list

    print(banner("MEMOIZED-CUT-ROD trace,  n = %d" % n))
    if a.seed is not None:
        print("seed %d" % a.seed)
    print()
    print(price_table(p))

    print(banner("Phase 0 -- initialise", "-"))
    print("  Lines 2-3 set every box to -inf, box 0 included.")
    print(memo_line([NEG] * (n + 1), "r"))

    print(banner("Phase 1 -- the dive (no arithmetic yet)", "-"))
    print("  The loop starts at i = 1 and recurses on n - i, so every frame")
    print("  calls the frame one smaller before it computes anything. The")
    print("  descent below is therefore forced, and these %d misses are the"
          % (n + 1))
    print("  only misses in the whole run.")
    print()
    for k in range(n, -1, -1):
        note = ("n == 0, so q = 0; r[0] = 0; return 0" if k == 0
                else "r[%d] = -inf, so take i = 1 and call AUX(%d)"
                     % (k, k - 1))
        print("  %sAUX(%d)  MISS -> %s" % ("  " * (n - k), k, note))

    print(banner("Phase 2 -- the unwind (all the arithmetic)", "-"))
    print("  Frames finish smallest first. In each frame the i = 1 row is the")
    print("  call already made on the way down; every other row is a hit.")

    t = Tracer(p, n, step=a.step)
    result, _ = t.aux(n)

    assert t.dive == [(n - k, k) for k in range(n, -1, -1)], \
        "dive did not follow the predicted chain"

    print(banner("Result", "-"))
    print("  MEMOIZED-CUT-ROD(p, %d) = %d" % (n, result))
    print(memo_line(t.r, "final memo"))

    expected_calls = 1 + n * (n + 1) // 2
    print()
    print("  AUX invocations   %3d   (expected 1 + n(n+1)/2 = %d)"
          % (t.calls, expected_calls))
    print("  misses            %3d   (expected n + 1        = %d)"
          % (t.misses, n + 1))
    print("  hits              %3d   (expected n(n-1)/2     = %d)"
          % (t.hits, n * (n - 1) // 2))
    print("  max stack depth   %3d" % (n + 1))

    r, s = bottom_up(p, n)
    pieces = cuts(s, n)
    print(banner("Cross-check against BOTTOM-UP-CUT-ROD", "-"))
    print("  r[0..%d] = [%s]" % (n, ", ".join(str(v) for v in r)))
    print("  s[1..%d] = [%s]" % (n, ", ".join(str(v) for v in s[1:])))
    print("  optimal pieces: %s  ->  %s = %d"
          % (" + ".join(str(c) for c in pieces),
             " + ".join("p[%d]=%d" % (c, p[c - 1]) for c in pieces),
             sum(p[c - 1] for c in pieces)))
    ok = (r[n] == result and t.calls == expected_calls
          and t.misses == n + 1 and list(t.r) == r)
    print("  agreement: %s" % ("OK" if ok else "MISMATCH"))
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:      # e.g. piping into head
        sys.stderr.close()
        sys.exit(0)
