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


class MusicException(BaseFrameworkError):
	"""Class for all music exceptions"""
	pass


class AmbiguousChannelError(MusicException):
	"""Raised when it is ambiguous what voice channel is targeted."""
	pass


class UnknownChannelError(MusicException):
	"""Raised when the client does not know of any such voice channel."""
	pass


class NotConnectedException(MusicException):
	"""Raised when an operation is performed but the voice channel is not connected."""
	pass