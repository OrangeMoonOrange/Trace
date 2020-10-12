class Quote():
    def __init__(self,person,words):
        self.person=person
        self.words=words
    def who(self):
        return self.person
    def sys(self):
        return self.words+"."
