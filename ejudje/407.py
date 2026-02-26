class Reverse:
    def __init__(self, text):
        self.text = text
        self.index = len(text)

    def __iter__(self):
        return self

    def __next__(self):
        if self.index == 0:
            raise StopIteration
        self.index -= 1
        return self.text[self.index]


s = input()

for char in Reverse(s):
    print(char, end="")