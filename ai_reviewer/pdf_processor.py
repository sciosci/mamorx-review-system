import os
import json
import time
from bs4 import BeautifulSoup
from typing import Optional, Dict
from doc2json.grobid2json.grobid.grobid_client import GrobidClient
from doc2json.grobid2json.tei_to_json import convert_tei_xml_file_to_s2orc_json, convert_tei_xml_soup_to_s2orc_json
from pathlib import Path

PROJECT_HOME = Path(__file__).parent.parent

DEFAULT_GROBID_CONFIG = {
    "grobid_server": "ner.colorado.edu",
    "grobid_port": "80",
    "batch_size": 1000,
    "sleep_time": 5,
    "generateIDs": False,
    "consolidate_header": False,
    "consolidate_citations": False,
    "include_raw_citations": True,
    "include_raw_affiliations": False,
    "max_workers": 4,
}


class PdfProcessor:
    BASE_TEMP_DIR = str(PROJECT_HOME / 'output_files/temp')
    BASE_OUTPUT_DIR = str(PROJECT_HOME / 'output_files/papers_json')

    def __init__(self,
                 temp_dir: str = BASE_TEMP_DIR,
                 output_dir: str = BASE_OUTPUT_DIR,
                 grobid_config: Optional[Dict] = None
                 ):
        self.temp_dir = temp_dir
        self.output_dir = output_dir

        # Initialize grobid_config
        self.grobid_config = DEFAULT_GROBID_CONFIG.copy()
        if isinstance(grobid_config, dict):
            self.grobid_config.update(grobid_config)

        self._initialize_directories()

    def _initialize_directories(self):
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def process_pdf_stream(self, input_file: str, sha: str, input_stream: bytes) -> Dict:
        """
        Process PDF stream
        :param input_file:
        :param sha:
        :param input_stream:
        :return:
        """
        # Process PDF through Grobid -> TEI.XML
        client = GrobidClient(self.grobid_config)
        tei_text = client.process_pdf_stream(input_file, input_stream, self.temp_dir, "processFulltextDocument")

        # Make soup
        soup = BeautifulSoup(tei_text, "xml")

        # Get paper
        paper = convert_tei_xml_soup_to_s2orc_json(soup, input_file, sha)

        return paper.release_json('pdf')

    def process_pdf_file(self, input_file: str) -> str:
        """
        Process a PDF file and get JSON representation
        :param input_file:
        :return:
        """
        paper_id = '.'.join(input_file.split('/')[-1].split('.')[:-1])
        tei_file = os.path.join(self.temp_dir, f'{paper_id}.tei.xml')
        output_file = os.path.join(self.output_dir, f'{paper_id}.json')

        # Check if input file exists and output file doesn't
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"{input_file} doesn't exist")
        if os.path.exists(output_file):
            print(f'{output_file} already exists!')
            return output_file

        # Process PDF through Grobid -> TEI.XML
        client = GrobidClient(self.grobid_config)
        client.process_pdf(input_file, self.temp_dir, "processFulltextDocument")

        # Process TEI.XML -> JSON
        assert os.path.exists(tei_file)
        paper = convert_tei_xml_file_to_s2orc_json(tei_file)

        # Write to file
        with open(output_file, 'w') as outf:
            json.dump(paper.release_json(), outf, indent=4, sort_keys=False)

        return output_file

    def trial_run(self, input_file: str, keep_temp: bool = False) -> None:
        start_time = time.time()

        output_file = self.process_pdf_file(input_file)

        runtime = round(time.time() - start_time, 3)
        print("runtime: %s seconds " % (runtime))
        print(f'Output JSON file: {output_file}')
        print('done.')

        if not keep_temp:
            self._cleanup_temp()

    def _cleanup_temp(self):
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)


if __name__ == '__main__':
    print(str(PROJECT_HOME / 'output_files/temp'))

    processor = PdfProcessor()
    processor.trial_run("/home/tongzeng/Downloads/test.pdf", keep_temp=True)
