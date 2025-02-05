class MavlinkError(Exception):
    """
    Represents all errors related to MavComm
    """

    def __init__(self, message: str) -> None:
        """
        Constructor for MavCommError

        Args:
            message (str): description of the error
        """

        super().__init__()
        self.message = message

    def __str__(self) -> str:
        """
        Provides the representation of the error as a string

        Returns:
            str: representation of the error as a string
        """

        return f"MavlinkError: {self.message}"
