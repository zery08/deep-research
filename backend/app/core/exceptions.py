from fastapi import HTTPException, status


class SourceNotFoundError(HTTPException):
    def __init__(self, source_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source '{source_id}' not found",
        )


class ResearchJobNotFoundError(HTTPException):
    def __init__(self, job_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research job '{job_id}' not found",
        )


class OutlineNotFoundError(HTTPException):
    def __init__(self, outline_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outline '{outline_id}' not found",
        )


class SourceNotReadyError(HTTPException):
    def __init__(self, source_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Source '{source_id}' is not ready (still indexing or failed)",
        )


class IngestionError(Exception):
    def __init__(self, message: str, source_id: str | None = None) -> None:
        self.source_id = source_id
        super().__init__(message)


class UnsupportedFileTypeError(IngestionError):
    pass


class FileTooLargeError(IngestionError):
    pass


class ParseError(IngestionError):
    pass
