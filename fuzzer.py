#!/usr/bin/env python3
"""fuzzer - Simple fuzzer for finding crashes in functions."""
import sys, random, string, traceback

class FuzzResult:
    def __init__(self, input_data, error, traceback_str):
        self.input = input_data
        self.error = error
        self.traceback = traceback_str

class Fuzzer:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.crashes = []
        self.runs = 0
    def random_string(self, max_len=100):
        n = self.rng.randint(0, max_len)
        return "".join(self.rng.choice(string.printable) for _ in range(n))
    def random_bytes(self, max_len=100):
        n = self.rng.randint(0, max_len)
        return bytes(self.rng.randint(0, 255) for _ in range(n))
    def random_int(self, min_val=-2**31, max_val=2**31):
        return self.rng.randint(min_val, max_val)
    def random_json(self, depth=0):
        if depth > 3:
            return self.rng.choice([None, True, False, self.rng.randint(-100,100), self.random_string(10)])
        t = self.rng.randint(0, 5)
        if t == 0: return None
        if t == 1: return self.rng.randint(-1000, 1000)
        if t == 2: return self.random_string(20)
        if t == 3: return self.rng.random()
        if t == 4: return [self.random_json(depth+1) for _ in range(self.rng.randint(0,5))]
        return {self.random_string(5): self.random_json(depth+1) for _ in range(self.rng.randint(0,3))}
    def fuzz(self, func, generator, trials=1000):
        for _ in range(trials):
            self.runs += 1
            inp = generator()
            try:
                func(inp)
            except Exception as e:
                tb = traceback.format_exc()
                self.crashes.append(FuzzResult(inp, e, tb))
        return self.crashes

def test():
    f = Fuzzer(seed=42)
    # fuzz a parser that crashes on empty input
    def fragile_parser(s):
        if len(s) > 0 and s[0] == "!":
            raise ValueError("Bang!")
        return len(s)
    crashes = f.fuzz(fragile_parser, lambda: f.random_string(10), trials=500)
    assert len(crashes) > 0  # should find the ! crash
    assert any("Bang" in str(c.error) for c in crashes)
    # safe function
    f2 = Fuzzer(seed=42)
    crashes2 = f2.fuzz(lambda x: x * 2, lambda: f2.random_int(-100, 100), trials=100)
    assert len(crashes2) == 0
    print("OK: fuzzer")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: fuzzer.py test")
