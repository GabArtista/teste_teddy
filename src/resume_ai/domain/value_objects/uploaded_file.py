"""Value object representing an uploaded resume file."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UploadedFile:
    """Immutable representation of a user-supplied resume file."""

    filename: str
    content_type: str
    data: bytes

    def extension(self) -> str:
        """Return file extension in lower case."""

        return self.filename.split(".")[-1].lower()

