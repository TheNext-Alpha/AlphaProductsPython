class ValidationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class NotFoundError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class DatabaseError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
