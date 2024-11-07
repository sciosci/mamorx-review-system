from typing import Any
from crewai_tools import FileReadTool

class FileReadToolUTF8(FileReadTool):
    def _run(
        self,
        **kwargs: Any,
    ) -> Any:
        try:
            file_path = kwargs.get('file_path', self.file_path)
            with open(file_path, 'r', encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            return f"Fail to read the file {file_path}. Error: {e}"