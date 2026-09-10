#!/usr/bin/env python3
"""
Trace engines for the two CLRS rod-cutting DP algorithms, instrumented so
that every intermediate value shown in the workbook and answer key is
produced by actually executing the algorithm.

Pseudocode followed verbatim from the course slides (topic_4_DP_cutrod):

BOTTOM-UP-CUT-ROD(p, n)          EXTENDED-BOTTOM-UP-CUT-ROD(p, n)
  let r[0..n] be a new array       let r[0..n] and s[0..n] be new arrays
  r[0] = 0                         r[0] = 0
  for j = 1 to n                   for j = 1 to n
      q = -inf                         q = -inf
      for i = 1 to j                   for i = 1 to j
          q = max(q,p[i]+r[j-i])           if q < p[i] + r[j-i]
      r[j] = q                                 q = p[i] + r[j-i]
  return r[n]                                  s[j] = i
                                       r[j] = q
                                   return r and s

MEMOIZED-CUT-ROD-AUX(p, n, r)
  1 if r[n] >= 0
  2     return r[n]
  3 if n == 0
  4     q = 0
  5 else q = -inf
  6     for i = 1 to n
  7         q = max(q, p[i] + MEMOIZED-CUT-ROD-AUX(p, n-i, r))
  8 r[n] = q
  9 return q
"""

NEG = float("-inf")


# --------------------------------------------------------------- bottom-up

def bottom_up(p, n):
    """Run EXTENDED-BOTTOM-UP-CUT-ROD, recording every inner-loop step.

    p is 1-indexed conceptually; caller passes p[1..n] as a list, and this
    function indexes it as p[i-1].

    Returns (r, s, blocks) where blocks[j-1] is a dict describing the j-block:
        j, rows: list of per-i dicts {i, p_i, r_ji, total, q_before, q_after,
                                      updated}
        r_j, s_j
    """
    r = [0] + [None] * n
    s = [0] * (n + 1)
    blocks = []
    for j in range(1, n + 1):
        q = NEG
        rows = []
        for i in range(1, j + 1):
            q_before = q
            total = p[i - 1] + r[j - i]
            updated = q < total
            if updated:
                q = total
                s[j] = i
            rows.append({
                "i": i, "p_i": p[i - 1], "r_ji": r[j - i], "j_minus_i": j - i,
                "total": total, "q_before": q_before, "q_after": q,
                "updated": updated,
            })
        r[j] = q
        blocks.append({"j": j, "rows": rows, "r_j": r[j], "s_j": s[j],
                       "r_snapshot": list(r)})
    return r, s, blocks


def cut_list(s, n):
    """PRINT-CUT-ROD-SOLUTION: the multiset of piece lengths, in output order."""
    out = []
    while n > 0:
        out.append(s[n])
        n -= s[n]
    return out


# ----------------------------------------------------------------- top-down

class MemoTrace:
    """Runs MEMOIZED-CUT-ROD and records the full call sequence."""

    def __init__(self, p, n):
        self.p = p
        self.n = n
        self.r = [NEG] * (n + 1)          # line 2-3 of MEMOIZED-CUT-ROD
        self.events = []                   # flat, ordered log
        self.frames = []                   # one entry per *miss* (real frame)
        self.calls = 0
        self.hits = 0
        self.misses = 0
        self.depth = 0
        self.result = self._aux(n)

    def _aux(self, n):
        self.calls += 1
        depth = self.depth
        if self.r[n] >= 0:                                     # line 1
            self.hits += 1
            self.events.append({"kind": "hit", "n": n, "value": self.r[n],
                                "depth": depth})
            return self.r[n]                                   # line 2
        self.misses += 1
        frame = {"n": n, "depth": depth, "rows": [], "base": n == 0,
                 "order": len(self.frames)}
        self.frames.append(frame)
        self.events.append({"kind": "enter", "n": n, "depth": depth})
        if n == 0:                                             # line 3
            q = 0                                              # line 4
        else:
            q = NEG                                            # line 5
            for i in range(1, n + 1):                          # line 6
                self.depth = depth + 1
                before = self.r[n - i] >= 0
                sub = self._aux(n - i)                          # line 7
                self.depth = depth
                total = self.p[i - 1] + sub
                q_before = q
                q = max(q, total)
                frame["rows"].append({
                    "i": i, "p_i": self.p[i - 1], "sub_n": n - i,
                    "sub_val": sub, "memo_hit": before, "total": total,
                    "q_before": q_before, "q_after": q,
                    "updated": total > q_before,
                })
        self.r[n] = q                                          # line 8
        frame["r_n"] = q
        frame["r_snapshot"] = list(self.r)
        self.events.append({"kind": "return", "n": n, "value": q,
                            "depth": depth})
        return q                                               # line 9

    def dive_chain(self):
        """The i=1 descent: n, n-1, ..., 0 (order in which frames open)."""
        return [f["n"] for f in self.frames]

    def unwind_order(self):
        """Frames in the order they finish (0, 1, 2, ..., n)."""
        return sorted((f for f in self.frames), key=lambda f: f["n"])


def fmt(v):
    return "-inf" if v == NEG else str(v)


# ------------------------------------------------------------------- checks

if __name__ == "__main__":
    # Verify against the lecture-slide example: p = 1,5,8,9 ; n = 4 ; r4 = 10
    p = [1, 5, 8, 9]
    r, s, blocks = bottom_up(p, 4)
    assert r == [0, 1, 5, 8, 10], r
    print("bottom-up r =", r, " s =", s[1:], " cuts =", cut_list(s, 4))
    for b in blocks:
        print(f"j = {b['j']}")
        for row in b["rows"]:
            print(f"    i = {row['i']} -> q = max({fmt(row['q_before'])}, "
                  f"{row['total']})  = {row['q_after']}")
        print(f"  r[{b['j']}] = {b['r_j']}")

    m = MemoTrace(p, 4)
    assert m.result == 10, m.result
    print("\ntop-down result =", m.result, "calls =", m.calls,
          "hits =", m.hits, "misses =", m.misses)
    print("dive:", m.dive_chain())
    # cross-check both algorithms on many random tables
    import random
    random.seed(7)
    for _ in range(500):
        n = random.randint(1, 9)
        pr = sorted(random.sample(range(1, 40), n))
        rr, ss, _ = bottom_up(pr, n)
        mm = MemoTrace(pr, n)
        assert rr[n] == mm.result, (pr, n, rr, mm.result)
        assert sum(pr[k - 1] for k in cut_list(ss, n)) == rr[n]
        assert mm.calls == 1 + n * (n + 1) // 2, (n, mm.calls)
        assert mm.misses == n + 1
    print("cross-check on 500 random price tables: OK")
