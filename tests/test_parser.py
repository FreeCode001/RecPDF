import os
import sys
from recpdf import parse_pdf, refine_markdown

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

pdf_path = f'{root_dir}/examples/test1.pdf'
output_dir = f'{root_dir}/examples/output/'


def test_parse_pdf():
    content, rect_images = parse_pdf(pdf_path, output_dir)
    print(content)
    print(rect_images)

def test_refine_markdown():
    markdown = f'{output_dir}/test1/test1.md'
    refined_markdown = refine_markdown(markdown)
    print(refined_markdown)

if __name__ == '__main__':
    #test_parse_pdf()
    test_refine_markdown()