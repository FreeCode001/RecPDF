from .parser import parse_pdf, refine_markdown

# Version information
try:
    from importlib.metadata import version
    __version__ = version("recpdf")
except ImportError:
    # Fallback for Python < 3.8
    __version__ = "0.0.0"