from typing import Optional, Dict
from pathlib import Path
from bs4 import BeautifulSoup

from grobid_client.grobid_client import GrobidClient
from MAMORX.utils import load_grobid_config
from MAMORX.schemas import GrobidConfig
from MAMORX.utils.doc2json.grobid2json.tei_to_json import convert_tei_xml_soup_to_s2orc_json

class PDFProcessor:
    def __init__(self,
                 output_dir: str,
                 grobid_config: Optional[GrobidConfig] = None,
                 grobid_config_file_path: Optional[str] = "config/grobid_config.json",
                 grobid_server_url: Optional[str] = None
                 ):
        # Make output directory
        self.output_dir_base = Path(output_dir)
        self.temp_dir = Path(f"{output_dir}/tmp")

        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Initialize grobid_config
        if(grobid_config != None):
            self.grobid_config: GrobidConfig = grobid_config
        else:
            self.grobid_config: GrobidConfig = load_grobid_config(grobid_config_file_path)

        # Override grobid_server_url if specified
        if(grobid_server_url != None):
            self.grobid_config["grobid_server"] = grobid_server_url

        # Create grobid client
        self.grobid_client = GrobidClient(**self.grobid_config)


    def process_pdf_file(self, input_file_path: str) -> Dict[str, str]:
        """
        Process a PDF file and get JSON representation
        :param input_file:
        :return: PDF file content in JSON s2orc format 
        """
        # Process PDF through Grobid -> TEI.XML string
        source_path, status_code, tei_xml = self.grobid_client.process_pdf(
            "processFulltextDocument",
            input_file_path,
            tei_coordinates=True, 
            generateIDs=False,
            consolidate_header=False,
            consolidate_citations=False,
            include_raw_citations=True,
            include_raw_affiliations=False,
            segment_sentences=False
        )

        paper_id = source_path.split('/')[-1].split('.')[0]

        pdf_hash = "" # Placeholder

        # Process TEI.XML -> JSON
        tei_soup = BeautifulSoup(tei_xml, "xml")
        paper = convert_tei_xml_soup_to_s2orc_json(tei_soup, paper_id, pdf_hash)

        return paper.release_json()

