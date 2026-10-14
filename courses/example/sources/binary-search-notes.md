# Binary search: notes

These notes are the reading for the example unit. They are original and short on purpose; a real
course would point its units at book chapters or papers in this directory.

## 1. The invariant

Binary search finds a target in a sorted array by keeping a half-open interval `[lo, hi)` that is
guaranteed to contain the target if the target is present. Every step looks at the middle element
`mid = lo + (hi - lo) // 2` and discards the half that cannot contain the target. The loop ends
when the interval is empty.

The invariant is what makes the algorithm correct: if the target was in `[lo, hi)` before a step,
it is still in the new interval after it.

## 2. Why it takes about log2(n) steps

Each step at least halves the interval, so after `k` steps at most `n / 2^k` elements remain. The
interval is empty once `2^k > n`, which takes `floor(log2 n) + 1` steps in the worst case.

## 3. Off-by-one errors

Most bugs come from mixing interval conventions: using `hi = len(a)` (half-open) with the update
`hi = mid - 1` (closed), or the reverse. With a half-open interval the updates are `lo = mid + 1`
and `hi = mid`, and the loop condition is `lo < hi`.

## 4. Overflow

In languages with fixed-width integers, `(lo + hi) / 2` can overflow when both are large;
`lo + (hi - lo) / 2` cannot. The bug sat in widely used library code for years before it was
noticed.

## 5. Lower bound instead of membership

A variant returns the first index whose element is not less than the target (the "lower bound").
It answers membership, insertion position and counting (upper bound minus lower bound) with one
routine, and it never needs an equality test inside the loop.

## 6. Searching on the answer

The same idea works on any monotone predicate, not only on arrays: if `ok(x)` is false up to some
point and true after it, binary search over `x` finds the boundary. "The smallest capacity that
ships all packages in D days" is a typical example.
