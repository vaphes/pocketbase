from httpx._types import FileTypes
from typing import Sequence, Union

FileUploadTypes = Union[FileTypes, Sequence[FileTypes]]


class FileUpload:
    def __init__(self, *args):
        self.files: FileUploadTypes = args

    def get(self, key: str):
        if isinstance(self.files[0], Sequence) and not isinstance(self.files[0], str):
            return tuple((key, i) for i in self.files)
        return ((key, self.files),)
