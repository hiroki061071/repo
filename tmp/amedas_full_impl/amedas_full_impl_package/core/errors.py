class UserReadableError(Exception):
    """画面表示向け例外"""

class CsvStructureError(UserReadableError):
    pass

class NoDataError(UserReadableError):
    pass

class ValidationError(UserReadableError):
    pass
