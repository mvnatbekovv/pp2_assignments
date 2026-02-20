def multiply_all(multiplier, *numbers):
    result = []
    for num in numbers:
        result.append(num * multiplier)
    return result