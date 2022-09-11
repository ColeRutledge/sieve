class SystemException(Exception):
    def __init__(self, message: str, *args: tuple, extra: dict | None = None):
        super().__init__(message, *args)
        self.message = message
        self.extra = extra
