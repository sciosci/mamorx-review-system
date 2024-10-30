from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class articleToAnalyze(_message.Message):
    __slots__ = ("pdf", "title", "abstract")
    PDF_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    ABSTRACT_FIELD_NUMBER: _ClassVar[int]
    pdf: bytes
    title: str
    abstract: str
    def __init__(self, pdf: _Optional[bytes] = ..., title: _Optional[str] = ..., abstract: _Optional[str] = ...) -> None: ...

class figureAnalysisResult(_message.Message):
    __slots__ = ("success", "assessment")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ASSESSMENT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    assessment: str
    def __init__(self, success: bool = ..., assessment: _Optional[str] = ...) -> None: ...
