class WrongMagicCookieError(Exception):
    """Exception raised for incorrect magic cookie."""

    def __init__(self, message="Wrong magic cookie"):
        self.message = message
        super().__init__(self.message)


class WrongMessageTypeError(Exception):
    """Exception raised for incorrect message type."""

    def __init__(self, message="Wrong message type"):
        self.message = message
        super().__init__(self.message)


class InputTimeout(Exception):
    """Exception raised for input timeout."""

    def __init__(self, message="Input Timeout Occurred"):
        self.message = message
        super().__init__(self.message)
