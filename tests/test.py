import os
import sys
from time import sleep
from dotenv import load_dotenv

load_dotenv('.env')

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

pdf_path = f'{root_dir}/examples/test3.pdf'
output_dir = f'{root_dir}/examples/output/'
workers = 1
api_key = os.getenv('VLM_API_KEY')
base_url = os.getenv('VLM_API_BASE')
model = os.getenv('VLM_API_MODEL')

api_key2 = os.getenv('sf_api_key')
base_url2 = os.getenv('sf_api_base')
model2 = os.getenv('sf_api_model')

def test_parse_pdf():
    from recpdf import parse_pdf
    content, rect_images = parse_pdf(pdf_path, output_dir, api_key, base_url, model, workers)
    print(content)
    print(rect_images)

def test_refine_markdown():
    from recpdf import refine_markdown
    markdown = f'{output_dir}/test3/test3.md'
    refined_markdown = refine_markdown(markdown, api_key2, base_url2, model2)
    print(refined_markdown)

if __name__ == '__main__':
    test_parse_pdf()
    sleep(5)
    test_refine_markdown()