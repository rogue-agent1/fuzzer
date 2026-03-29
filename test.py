from fuzzer import Fuzzer, fuzz_test, shrink_int, shrink_list
f = Fuzzer(42)
assert isinstance(f.int(), int)
assert isinstance(f.string(), str)
assert isinstance(f.bool(), bool)
assert isinstance(f.list(lambda: f.int()), list)
failures = fuzz_test(lambda x: None, lambda fz: fz.int(), trials=100)
assert len(failures) == 0
assert 0 in shrink_int(5)
assert len(shrink_list([1,2,3])) > 0
print("Fuzzer tests passed")