#!/usr/bin/env python3
"""Property-based fuzzer. Zero dependencies."""
import random, sys, string, traceback

class Fuzzer:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def int(self, lo=-1000, hi=1000): return self.rng.randint(lo, hi)
    def float(self, lo=-1e6, hi=1e6): return self.rng.uniform(lo, hi)
    def bool(self): return self.rng.choice([True, False])
    def char(self): return self.rng.choice(string.printable)

    def string(self, min_len=0, max_len=50):
        n = self.rng.randint(min_len, max_len)
        return "".join(self.char() for _ in range(n))

    def list(self, gen, min_len=0, max_len=20):
        n = self.rng.randint(min_len, max_len)
        return [gen() for _ in range(n)]

    def choice(self, items): return self.rng.choice(items)

    def one_of(self, *gens): return self.rng.choice(gens)()

def fuzz_test(fn, gen, trials=100, seed=None):
    f = Fuzzer(seed)
    failures = []
    for i in range(trials):
        try:
            args = gen(f)
            if isinstance(args, tuple): fn(*args)
            else: fn(args)
        except AssertionError as e:
            failures.append({"trial": i, "args": args, "error": str(e)})
        except Exception as e:
            failures.append({"trial": i, "args": str(args)[:100], "error": traceback.format_exc()})
    return failures

def property_test(trials=100, seed=None):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        wrapper._fuzz_trials = trials
        wrapper._fuzz_seed = seed
        return wrapper
    return decorator

def shrink_int(n):
    if n == 0: return []
    candidates = [0, n//2, n-1 if n > 0 else n+1]
    return [c for c in candidates if c != n]

def shrink_list(lst):
    if not lst: return []
    candidates = [lst[1:], lst[:-1]]
    for i in range(len(lst)):
        candidates.append(lst[:i] + lst[i+1:])
    return candidates

if __name__ == "__main__":
    def prop_sort_idempotent(lst):
        assert sorted(sorted(lst)) == sorted(lst)
    f = Fuzzer(42)
    failures = fuzz_test(prop_sort_idempotent, lambda fz: fz.list(lambda: fz.int(-100,100)), trials=1000)
    print(f"Sort idempotent: {1000-len(failures)}/1000 passed, {len(failures)} failures")
