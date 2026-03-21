"""Calendar-specific exceptions."""


class CalendarSyncError(Exception):
    """Raised when a calendar synchronization operation fails.

    This covers failures during create, update, delete, or list operations
    against any calendar provider.
    """

    def __init__(self, message: str = "Calendar sync operation failed") -> None:
        self.message = message
        super().__init__(self.message)


class CalendarAuthError(Exception):
    """Raised when calendar authentication or authorization fails.

    This covers invalid credentials, expired tokens, or insufficient
    permissions when connecting to a calendar provider.
    """

    def __init__(self, message: str = "Calendar authentication failed") -> None:
        self.message = message
        super().__init__(self.message)
