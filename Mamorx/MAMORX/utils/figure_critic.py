from MAMORX.schemas import APIConfigs

class FigureCriticClient(object):
    def __init__(self, api_config: APIConfigs):
        # self.stub = server(api_config["figure_critic_url"])
        self.stub = None

    def critic_pdf_file(self, pdf_file_path: str, title: str, abstract: str) -> str:
        # Open and load PDF file and bytes
        with open(pdf_file_path, "rb") as f:
            pdf_file_bytes = f.read()

        # Send PDF_file along with title and abstract
        result = "sample figure critic"#self.stub.some_function(pdf_file_bytes, title, abstract)
        return result