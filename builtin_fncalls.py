def sumofthreecubes(a, b, c):
    return pow(a, 3) + pow(b, 3) + pow(c, 3)

def diff(a, b, c):
    return abs(pow(a+b+c, 3) - sumofthreecubes(a, b, c))

print(diff(7,6,5))