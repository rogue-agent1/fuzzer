#!/usr/bin/env python3
"""fuzzer - Simple fuzzer for function testing with mutation strategies."""
import sys, random

def fuzz_bytes(seed=b"", length=100, mutations=10):
    data = bytearray(seed or bytes(random.randint(0, 255) for _ in range(length)))
    for _ in range(mutations):
        strategy = random.choice(["flip", "insert", "delete", "replace"])
        if not data: data = bytearray([random.randint(0, 255)])
        if strategy == "flip":
            idx = random.randint(0, len(data)-1)
            bit = random.randint(0, 7)
            data[idx] ^= (1 << bit)
        elif strategy == "insert":
            idx = random.randint(0, len(data))
            data.insert(idx, random.randint(0, 255))
        elif strategy == "delete" and len(data) > 1:
            idx = random.randint(0, len(data)-1)
            del data[idx]
        elif strategy == "replace":
            idx = random.randint(0, len(data)-1)
            data[idx] = random.randint(0, 255)
    return bytes(data)

def fuzz_string(seed="", charset=None, length=50, mutations=5):
    chars = charset or [chr(i) for i in range(32, 127)]
    s = list(seed or [random.choice(chars) for _ in range(length)])
    for _ in range(mutations):
        if not s: s = [random.choice(chars)]
        strategy = random.choice(["replace", "insert", "delete"])
        if strategy == "replace":
            s[random.randint(0, len(s)-1)] = random.choice(chars)
        elif strategy == "insert":
            s.insert(random.randint(0, len(s)), random.choice(chars))
        elif strategy == "delete" and len(s) > 1:
            del s[random.randint(0, len(s)-1)]
    return "".join(s)

def fuzz_test(fn, gen, trials=1000, seed=None):
    if seed is not None: random.seed(seed)
    crashes = []
    for i in range(trials):
        inp = gen()
        try:
            fn(inp)
        except Exception as e:
            crashes.append({"trial": i, "input": inp, "error": str(e)})
    return crashes

def test():
    random.seed(42)
    b = fuzz_bytes(length=10, mutations=3)
    assert isinstance(b, bytes) and len(b) > 0
    s = fuzz_string(length=10, mutations=2)
    assert isinstance(s, str) and len(s) > 0
    def safe_fn(x): return len(x)
    crashes = fuzz_test(safe_fn, lambda: fuzz_bytes(length=20), trials=100, seed=42)
    assert len(crashes) == 0
    def crashy_fn(x):
        if len(x) > 5 and x[0] < 50: raise ValueError("crash")
    crashes2 = fuzz_test(crashy_fn, lambda: fuzz_bytes(length=20), trials=100, seed=42)
    assert len(crashes2) > 0
    print("fuzzer: all tests passed")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("Usage: fuzzer.py --test")
