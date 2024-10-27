from crewai_tools import BaseTool
from typing import Any, Optional

class TextContainerTool(BaseTool):
    name:str = "text-container-tool"
    description:str = "A tool that contains text"
    content: Optional[str] = None


    def __init__(self, content: Optional[str], **kwargs):
        super().__init__(**kwargs)
        if(content is not None):
            self.content = content


    def _run(
            self, 
            **kwargs: Any
    ) -> Optional[str]:
        content = kwargs.get("content", self.content)
        return content
