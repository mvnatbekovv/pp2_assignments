class Student:
    def __init__(self, name, group, gpa):
        # self — это конкретный объект
        self.name = name
        self.group = group
        self.gpa = gpa

    def info(self):
        return f"{self.name} ({self.group}), GPA: {self.gpa}"
