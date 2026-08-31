class UnicornException(Exception):
    def __init__(
        self,
        status_code: int,
        err_description: str
    ):
        self.status_code = status_code
        self.err_description = err_description

class SerializerException(Exception):
    pass