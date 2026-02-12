from .parser import parse_pdf, refine_markdown
from .translator import translate_markdown, translate_text
from .config import Settings

__all__ = [parse_pdf, refine_markdown, translate_markdown, translate_text, Settings]

# Version information
try:
    from importlib.metadata import version
    __version__ = version("recpdf")
except ImportError:
    # Fallback for Python < 3.8
    __version__ = "0.0.0"