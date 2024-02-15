import contextvars
import uuid


class TraceIdException(Exception):
    """
    Base class for all TraceId exceptions.
    """

    pass


class TraceIdNotYetSetError(TraceIdException):
    """
    Raised when trying to get a traceid that hasn't been set.
    Please use TraceId.gen() to generate a new traceid or TraceId.set() to set an existing traceid.
    """

    pass


class TraceIdAlreadySetError(TraceIdException):
    """
    Raised when trying to set a traceid that has already been set.
    """

    pass


class TraceId(object):
    traceid_var = contextvars.ContextVar[uuid.UUID | str]("__traceid__")

    @classmethod
    def set(cls, traceid: uuid.UUID | str, coverage: bool = False) -> None:
        """
        Set the traceid for the current context.
        Args:
            traceid: The traceid to set. Cannot be None.
        Returns:
            None
        """
        if traceid is None:  # type: ignore
            raise ValueError("TraceId cannot be set to None.")
        if not coverage and cls.is_set():
            raise TraceIdAlreadySetError(
                "TraceId is already set. Please use TraceId.clear() to clear the traceid."
            )
        cls.traceid_var.set(traceid)

    @classmethod
    def get(cls) -> uuid.UUID | str:
        """
        Get the traceid for the current context.
        Returns:
            The traceid for the current context.
        """
        try:
            id = cls.traceid_var.get()
            if id is None:  # type: ignore
                raise TraceIdNotYetSetError(
                    "TraceId is not yet set. Please use TraceId.gen() to generate a new traceid or TraceId.set() to set an existing traceid."
                )
            return id
        except LookupError:
            raise TraceIdNotYetSetError(
                "TraceId is not yet set. Please use TraceId.gen() to generate a new traceid or TraceId.set() to set an existing traceid."
            )

    @classmethod
    def clear(cls) -> None:
        """
        Clear the traceid for the current context.
        Returns:
            None
        """
        cls.traceid_var.set(None)  # type: ignore

    @classmethod
    def is_set(cls) -> bool:
        """
        Check if the traceid is set for the current context.
        Returns:
            True if the traceid is set, False otherwise.
        """
        return cls.traceid_var.get(None) is not None

    @classmethod
    def gen(cls):
        """
        Generate and set a new traceid.
        """
        if not cls.is_set():
            cls.set(uuid.uuid4())
