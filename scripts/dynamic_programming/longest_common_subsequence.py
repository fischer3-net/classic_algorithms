from __future__ import annotations


def lcs_length(first: str, second: str) -> int:
    """Return the length of the longest common subsequence, not the subsequence itself."""
    rows = len(first) + 1
    cols = len(second) + 1
    table = [[0] * cols for _ in range(rows)]

    for i in range(1, rows):
        for j in range(1, cols):
            if first[i - 1] == second[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = max(table[i - 1][j], table[i][j - 1])

    return table[-1][-1]


def main() -> None:
    first = "algorithm"
    second = "alligator"
    length = lcs_length(first, second)
    print(f"LCS length between '{first}' and '{second}': {length}")


if __name__ == "__main__":
    main()
