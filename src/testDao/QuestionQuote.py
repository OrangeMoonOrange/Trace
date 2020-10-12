from Quote import Quote
class QuestionQuote(Quote):
    def sys(self):
        return self.words+"?"


if __name__ == '__main__':
    quote = QuestionQuote("KAIKAI", "TEXT")
    print quote.sys()
