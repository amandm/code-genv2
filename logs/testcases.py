#!/usr/bin/env python3
import timeit

def test_performance():
    for i in range(100000):
        find_golden_ratio(10)

print(timeit.timeit(test_performance, number=100))