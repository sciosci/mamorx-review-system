from crewai_tools import BaseTool


class FigureTool(BaseTool):
    name:str = "figure-tool"
    description:str = ""


    def __init__(self, pdf_file_path: str, **kwargs):
        super().__init__(**kwargs)


    def _run(self) -> str:
        return ""