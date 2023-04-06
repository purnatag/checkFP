def init_val(arg1):
    return arg1
def fib(n):
    if n == 0 or n == 1:
        return init_val(n)
    return fib(n-1) + fib(n-2)

print(fib(15))
