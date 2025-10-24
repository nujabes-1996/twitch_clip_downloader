class AuthenticationError(Exception):
    def __init__(self, message, filename=None, lineno=None):
        super().__init__(message)
        self.message = message
        self.filename = filename
        self.lineno = lineno

    def __str__(self):
        details = []
        if self.message:
            details.append(str(self.message))
        if self.filename:
            details.append(f"in {self.filename}")
        if self.lineno:
            details.append(f"at line {self.lineno}")
        return " ".join(details)