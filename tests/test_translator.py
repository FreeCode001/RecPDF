from recpdf import translate_markdown, Settings
import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

input_markdown = f'{root_dir}/examples/output/test1/test1_refined.md'
output_markdown = f'{root_dir}/examples/output/test1/'

if __name__ == "__main__":
    settings = Settings()
    settings.translation_engine = "openai"
    result = translate_markdown(input_markdown, output_markdown, settings=settings)
    print(result)
