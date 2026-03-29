#!/usr/bin/env python3
"""fuzzer: Property-based testing / fuzzing framework."""
import random, sys, traceback

class Fuzzer:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.failures = []

    def gen_int(self, lo=-1000, hi=1000): return self.rng.randint(lo, hi)
    def gen_float(self, lo=-1000, hi=1000): return self.rng.uniform(lo, hi)
    def gen_str(self, max_len=20):
        n = self.rng.randint(0, max_len)
        return "".join(chr(self.rng.randint(32, 126)) for _ in range(n))
    def gen_list(self, gen_elem, max_len=20):
        n = self.rng.randint(0, max_len)
        return [gen_elem() for _ in range(n)]
    def gen_bool(self): return self.rng.choice([True, False])
    def gen_choice(self, options): return self.rng.choice(options)

    def check(self, prop, gen_args, trials=100):
        for i in range(trials):
            args = gen_args(self)
            try:
                result = prop(*args)
                if result is False:
                    self.failures.append({"trial": i, "args": args, "error": "returned False"})
                    return False
            except Exception as e:
                self.failures.append({"trial": i, "args": args, "error": str(e)})
                return False
        return True

    def shrink_int(self, n):
        candidates = [0]
        if n > 0: candidates.extend([n//2, n-1])
        if n < 0: candidates.extend([n//2, n+1])
        return candidates

def test():
    f = Fuzzer(seed=42)
    # Sort is idempotent
    assert f.check(
        lambda lst: sorted(sorted(lst)) == sorted(lst),
        lambda f: (f.gen_list(lambda: f.gen_int(-100,100)),),
        trials=50
    )
    # Reverse reverse = identity
    assert f.check(
        lambda lst: list(reversed(list(reversed(lst)))) == lst,
        lambda f: (f.gen_list(lambda: f.gen_int()),),
        trials=50
    )
    # Deliberate failure
    f2 = Fuzzer(seed=0)
    result = f2.check(
        lambda n: n < 50,
        lambda f: (f.gen_int(0, 100),),
        trials=200
    )
    assert not result
    assert len(f2.failures) > 0
    # Generators
    f3 = Fuzzer(seed=1)
    assert isinstance(f3.gen_str(), str)
    assert isinstance(f3.gen_float(), float)
    assert f3.gen_bool() in (True, False)
    # Shrink
    assert 0 in f3.shrink_int(10)
    assert 0 in f3.shrink_int(-5)
    print("All tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Usage: fuzzer.py test")
