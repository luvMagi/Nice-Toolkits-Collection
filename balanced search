from typing import List, Optional, Tuple

def find_balanced(text: str, left: str = "(", right: str = ")",
                  start: int = 0) -> Optional[Tuple[int, int, str]]:
    """Find the first balanced region starting at/after `start`.

    This finds the first `left` at/after `start`, then scans forward:
    - depth += 1 on `left`
    - depth -= 1 on `right`
    When depth returns to 0, we found the matching `right`.

    Args:
        text: Source string.
        left: Left delimiter (may be multi-char, e.g. '（').
        right: Right delimiter (may be multi-char, e.g. '）').
        start: Search starting index.

    Returns:
        (i_left, i_right, inner) where:
            i_left  = index of the first char of `left`
            i_right = index of the first char of the matching `right`
            inner   = text between them (exclusive)
        If not found or unbalanced, returns None.

    Notes:
        - Overlapping pairs are not produced here; this returns only the first.
        - Works with fullwidth punctuations (e.g., '（', '）').
    """
    if not left or not right:
        raise ValueError("left/right must be non-empty strings.")
    n, L, R = len(text), len(left), len(right)

    # 1) 找到起始 left
    i = text.find(left, start)
    if i < 0:
        return None

    depth = 0
    j = i
    while j < n:
        # 优先检查 left/right 子串匹配（多字符安全）
        if text.startswith(left, j):
            depth += 1
            j += L
            continue
        if text.startswith(right, j):
            depth -= 1
            if depth == 0:
                # j 是 right 的起始
                inner = text[i + L : j]
                return (i, j, inner)
            j += R
            continue
        # 普通字符，前进一步
        j += 1

    # 扫到底仍未闭合
    return None


def find_all_balanced(text: str, left: str = "(", right: str = ")",
                      start: int = 0) -> List[Tuple[int, int, str]]:
    """Find all non-overlapping balanced regions in `text`.

    Iteratively calls `find_balanced` and advances beyond each match.

    Returns:
        A list of (i_left, i_right, inner).
    """
    results: List[Tuple[int, int, str]] = []
    pos = start
    while True:
        found = find_balanced(text, left, right, pos)
        if not found:
            break
        i_left, i_right, inner = found
        results.append(found)
        # 跳过当前这对（非重叠）
        pos = i_right + len(right)
    return results
