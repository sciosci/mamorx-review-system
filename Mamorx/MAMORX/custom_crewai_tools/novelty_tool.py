from crewai_tools import BaseTool


class NoveltyTool(BaseTool):
    name:str = "novelty-tool"
    description:str = ""


    def __init__(self, pdf_file_path: str, **kwargs):
        super().__init__(**kwargs)


    def _run(self) -> str:
        return ""