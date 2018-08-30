"""Exceptions that are used in the framework"""


class BaseFrameworkError(Exception):
	"""Base exception for all custom errors."""
	pass


class UserBotError(BaseFrameworkError):
	"""Raised when framework is run with a user account."""
	pass


class HandlerError(BaseFrameworkError):
	"""Raised when there is a problem with a handler function."""
	pass


class TimerException(BaseFrameworkError):
	"""Raised when the command timer has an exception."""
	pass
