class tokenReader:

    def __init__(self, tokens):
        self.currentPos = 0
        self.EOF = False
        self.SOF = True
        self.currentToken = tokens[0]
        self.tokens = tokens

    def forw(self, amt = 1):
        if amt < 0:
            return self.back(-amt)
        if amt == 0:
            return self.currentToken
        
        if self.EOF is False:
            if self.SOF is True:
                self.SOF = False
            self.currentPos = min(self.currentPos + amt, len(self.tokens) - 1)
            if self.currentPos + 1 >= len(self.tokens):
                self.EOF = True
            self.currentToken = self.tokens[self.currentPos]
        else:
            return None
        return self.currentToken

    def back(self, amt=1):
        if amt < 0:
            return self.forw(-amt)
        if amt == 0:
            return self.currentToken

        
        if self.SOF is False:
            if self.EOF is True:
                self.EOF = False
            self.currentPos = max(self.currentPos - amt, 0)
            if self.currentPos <= 0:
                self.SOF = True
            self.currentToken = self.tokens[self.currentPos]
        else:
            return None
        return self.currentToken
