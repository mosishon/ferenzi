




class BaseExceptions(Exception):
    """Base class for all exceptions.
    :param title: str - The message to display.
    :param code: int - The error code.
    :param details: str - The details of the error.
    """
    code:int = None
    title:str = None
    details:str = None
class NotFound(BaseExceptions):
    """The requested object was not found.
    :param title: str - The message to display.
    :param code: int - The error code.

    """
    code = 404
    title = "Not Found"

class AlreadyExists(BaseExceptions):
    """The requested object already exists.
    :param title: str - The message to display.
    :param code: int - The error code.

    """
    code = 409
    title = "Already Exists"

class InvalidError(BaseExceptions):
    """The requested object is invalid.
    :param title: str - The message to display.
    :param code: int - The error code.

    """
    code = 422
    title = "Invalid Error"

class GroupAlreadyExists(AlreadyExists):
    """The requested group already exists.
    :param details: str - The details of the error.

    """
    details = "The requested group already exists."

class GroupNotExists(NotFound):
    """The requested group does not exist.
    :param details: str - The details of the error.

    """
    details = "The requested group does not exist."

class ClientNotJoined(NotFound):
    """The client is not joined to the group.
    :param details: str - The details of the error.

    """
    details = "The client is not joined to the group."

class ClientAlreadyJoined(AlreadyExists):
    """The client is already joined to the group.
    :param details: str - The details of the error.

    """
    details = "The client is already joined to the group."

class InvalidInviteLink(InvalidError):
    """The invite link is invalid.
    :param details: str - The details of the error.

    """
    details = "The invite link is invalid."