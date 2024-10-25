from typing import Optional, Dict
# from doc2json.grobid2json.tei_to_json import convert_tei_xml_file_to_s2orc_json, convert_tei_xml_soup_to_s2orc_json
from pathlib import Path

from grobid_client.grobid_client import GrobidClient
from MAMORX.utils import load_grobid_config
from MAMORX.schemas import GrobidConfig


class PDFProcessor:
    def __init__(self,
                 output_dir: str,
                 grobid_config: Optional[GrobidConfig] = None,
                 grobid_config_file_path: Optional[str] = "config/grobid_config.json"
                 ):
        # Make output directory
        self.output_dir_base = Path(output_dir)
        self.temp_dir = Path(f"{output_dir}/tmp")
        self.parsed_output_dir = Path(f"{output_dir}/parsed_pdf")

        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.parsed_output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize grobid_config
        if(grobid_config != None):
            self.grobid_config: GrobidConfig = grobid_config
        else:
            self.grobid_config: GrobidConfig = load_grobid_config(grobid_config_file_path)

        # Create grobid client
        self.grobid_client = GrobidClient(**self.grobid_config)


    def process_pdf_file(self, input_file_path: str) -> str:
        """
        Process a PDF file and get JSON representation
        :param input_file:
        :return:
        """
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



        return ""
    #     paper_id = '.'.join(input_file.split('/')[-1].split('.')[:-1])
    #     tei_file = os.path.join(self.temp_dir, f'{paper_id}.tei.xml')
    #     output_file = os.path.join(self.output_dir, f'{paper_id}.json')

    #     # Check if input file exists and output file doesn't
    #     if not os.path.exists(input_file):
    #         raise FileNotFoundError(f"{input_file} doesn't exist")
    #     if os.path.exists(output_file):
    #         print(f'{output_file} already exists!')
    #         return output_file

    #     # Process PDF through Grobid -> TEI.XML
    #     self.grobid_client.process_pdf()
    #     client = GrobidClient(self.grobid_config)
    #     client.process_pdf(input_file, self.temp_dir, "processFulltextDocument")

    #     # Process TEI.XML -> JSON
    #     assert os.path.exists(tei_file)
    #     paper = convert_tei_xml_file_to_s2orc_json(tei_file)

    #     # Write to file
    #     with open(output_file, 'w') as outf:
    #         json.dump(paper.release_json(), outf, indent=4, sort_keys=False)

    #     return output_file

    # def trial_run(self, input_file: str, keep_temp: bool = False) -> None:
    #     start_time = time.time()

    #     output_file = self.process_pdf_file(input_file)

    #     runtime = round(time.time() - start_time, 3)
    #     print("runtime: %s seconds " % (runtime))
    #     print(f'Output JSON file: {output_file}')
    #     print('done.')

    #     if not keep_temp:
    #         self._cleanup_temp()

    # def _cleanup_temp(self):
    #     if os.path.exists(self.temp_dir):
    #         for file in os.listdir(self.temp_dir):
    #             os.remove(os.path.join(self.temp_dir, file))
    #         os.rmdir(self.temp_dir)


# if __name__ == '__main__':
#     processor = PdfProcessor()
#     processor.process_pdf_file("test.pdf")
#     processor.trial_run("test.pdf", keep_temp=True)
