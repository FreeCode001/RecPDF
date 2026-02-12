from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List


class Settings(BaseSettings):
    """RecPDF configuration settings"""
    # Parser config
    parser_api_key: str = Field(default="", description="Parser API key (optional)")
    parser_api_base: str = Field(default="", description="Parser API base URL (optional)")
    parser_api_model: str = Field(default="", description="Parser API model (optional)")
    # Refine config
    refine_api_key: str = Field(default="", description="Refine API key (optional)")
    refine_api_base: str = Field(default="", description="Refine API base URL (optional)")
    refine_api_model: str = Field(default="", description="Refine API model (optional)")
    # DeepL config
    deepl_api_key: str = Field(default="", description="DeepL API key (optional)")
    # HuggingFace config
    huggingface_model: str = Field(
        default="Helsinki-NLP/opus-mt-en-zh",
        description="HuggingFace model for translation",
    )
    # Translator config
    translation_engine: str = Field(
        default="googletrans",
        description="Translation engine: deepl, googletrans, huggingface, openai",
    )
    translator_api_key: str = Field(default="", description="Translator API key (optional)")
    translator_api_base: str = Field(default="", description="Translator API base URL (optional)")
    translator_api_model: str = Field(default="", description="Translator API model (optional)")
    

    # Maximum file size in MB
    max_file_size_mb: int = Field(
        default=50, ge=1, le=100, description="Maximum file size in MB"
    )
    # Supported languages
    supported_languages: str = Field(default="en,zh", description="Supported languages")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @field_validator("translation_engine", mode="before")
    @classmethod
    def validate_engine(cls, v):
        valid_engines = ["googletrans", "huggingface", "deepl", "openai"]
        if v not in valid_engines:
            raise ValueError(
                f"Invalid translation engine. Choose from: {valid_engines}"
            )
        return v


    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes"""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def language_list(self) -> List[str]:
        """Get supported languages as list"""
        return [lang.strip() for lang in self.supported_languages.split(",")]

    @property
    def use_deepl(self) -> bool:
        """Check if DeepL engine is configured"""
        return self.translation_engine == "deepl" and bool(self.deepl_api_key)


# Global settings instance
settings = Settings()
