"""mathutils — workload cho performance-engineer."""


def slow_sum(n: int) -> int:
    total = 0
    for i in range(n):
        total += i * i
    return total


def naive_fib(n: int) -> int:
    if n <= 1:
        return n
    return naive_fib(n - 1) + naive_fib(n - 2)


if __name__ == "__main__":
    print(slow_sum(200000))
    print(naive_fib(28))
