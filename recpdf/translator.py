import os
import re
import asyncio
import inspect
from typing import Dict, List, Any
from abc import ABC, abstractmethod
from .config import Settings
from .models import init_translator_model
from .prompts import DEFAULT_TRANSLATOR_PROMPT

"""
已实现翻译器：
    Google Translator
    DeepPL Translator
    HuggingFace Translator
    OpenAITranslator  # 兼容OpenAI API的平台都可以使用
待实现翻译器：
    ZhipuTranslator
    SiliconTranslator
    DeepseekTranslator
    GeminiTranslator
"""

class BaseTranslator(ABC):
    """Abstract base class for translators"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.max_chunk_size = 5000

    @abstractmethod
    async def translate_text(
        self, text: str, source_lang: str = "EN", target_lang: str = "ZH"
    ) -> Dict[str, Any]:
        """Translate text from source language to target language"""
        pass

    def _chunk_text(self, text: str, max_length: int) -> List[str]:
        """Split text into chunks of maximum length while preserving sentence boundaries"""
        if len(text) <= max_length:
            return [text]

        chunks = []
        sentences = re.split(r"(?<=[.!?。！？])\s+", text)
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk + sentence) <= max_length:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _detect_language(self, text: str) -> str:
        """Simple language detection based on character patterns"""
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        total_chars = len(re.sub(r"\s", "", text))

        if total_chars > 0 and chinese_chars / total_chars > 0.3:
            return "ZH"

        return "EN"  # Default to English


class GoogleTranslator(BaseTranslator):
    """Google Translator using googletrans library (free, no API key required)"""

    def __init__(self, settings: Settings):
        super().__init__(settings)
        self._translator = None

    async def _get_translator(self):
        """Get translator instance"""
        if self._translator is None:
            try:
                from googletrans import Translator

                # Create a new Translator instance
                self._translator = Translator()
            except ImportError:
                raise ImportError(
                    "googletrans library not installed. Install with: pip install googletrans>=4.0.2"
                )
        return self._translator

    async def translate_text(
        self, text: str, source_lang: str = "EN", target_lang: str = "ZH"
    ) -> Dict[str, Any]:
        """Translate text using Google Translate"""
        try:
            if not text.strip():
                return {"success": False, "error": "No text provided for translation"}

            # Detect source language if not provided
            if not source_lang:
                source_lang = self._detect_language(text)

            # Check if translation is needed
            if source_lang == target_lang:
                return {
                    "success": True,
                    "translated_text": text,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                }

            translator = await self._get_translator()

            # Split text into chunks if it's too long
            chunks = self._chunk_text(text, self.max_chunk_size)

            if len(chunks) == 1:
                # Single chunk translation
                result = await self._translate_single_chunk(
                    translator, chunks[0], source_lang, target_lang
                )
            else:
                # Multiple chunks translation
                result = await self._translate_multiple_chunks(
                    translator, chunks, source_lang, target_lang
                )

            return result

        except Exception as e:
            return {"success": False, "error": f"Google translation failed: {str(e)}"}

    async def _translate_single_chunk(
        self, translator, text: str, source_lang: str, target_lang: str
    ) -> Dict[str, Any]:
        """Translate a single chunk of text"""
        try:
            # Map language codes for Google Translate
            google_source = self._map_language_code(source_lang)
            google_target = self._map_language_code(target_lang)

            # Run translation - handle both sync and async cases
            try:
                # Check if translate is a coroutine function
                is_coroutine = inspect.iscoroutinefunction(translator.translate)
                
                if is_coroutine:
                    # It's async, await it directly
                    print("Translate in async mode")
                    result = await translator.translate(
                        text, src=google_source, dest=google_target
                    )
                    print(result)
                else:
                    # It's sync, run in executor
                    print("Translate in sync mode")
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: translator.translate(
                            text, src=google_source, dest=google_target
                        ),
                    )
            except Exception as e:
                # Handle any other errors
                return {
                    "success": False,
                    "error": f"Translation failed: {type(e).__name__}: {str(e)}"
                }

            return {
                "success": True,
                "translated_text": result.text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "chunks_translated": 1,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Single chunk translation failed: {str(e)}",
            }

    async def _translate_multiple_chunks(
        self, translator, chunks: List[str], source_lang: str, target_lang: str
    ) -> Dict[str, Any]:
        """Translate multiple chunks of text"""
        try:
            google_source = self._map_language_code(source_lang)
            google_target = self._map_language_code(target_lang)

            translated_chunks = []

            for chunk in chunks:
                # Run translation - handle both sync and async cases
                try:
                    # Check if translate is a coroutine function
                    is_coroutine = inspect.iscoroutinefunction(translator.translate)
                    
                    if is_coroutine:
                        # It's async, await it directly
                        result = await translator.translate(
                            chunk, src=google_source, dest=google_target
                        )
                    else:
                        # It's sync, run in executor
                        result = await asyncio.get_event_loop().run_in_executor(
                            None,
                            lambda c=chunk: translator.translate(
                                c, src=google_source, dest=google_target
                            ),
                        )
                except Exception as e:
                    # Handle any other errors
                    return {
                        "success": False,
                        "error": f"Translation failed in multiple chunks: {type(e).__name__}: {str(e)}"
                    }
                translated_chunks.append(result.text)

                # Add small delay to respect rate limits
                await asyncio.sleep(0.1)

            return {
                "success": True,
                "translated_text": " ".join(translated_chunks),
                "source_lang": source_lang,
                "target_lang": target_lang,
                "chunks_translated": len(chunks),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Multiple chunk translation failed: {str(e)}",
            }

    def _map_language_code(self, code: str) -> str:
        """Map language codes to Google Translate format"""
        mapping = {"EN": "en", "ZH": "zh-cn", "ZH-CN": "zh-cn", "ZH-TW": "zh-tw"}
        return mapping.get(code.upper(), code.lower())


class HuggingFaceTranslator(BaseTranslator):
    """HuggingFace Translator using local models (free, no API key required)"""

    def __init__(self, settings: Settings):
        super().__init__(settings)
        self._model = None
        self._tokenizer = None

    def _load_model(self):
        """Load translation model"""
        if self._model is None:
            try:
                from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

                print(f"Loading HuggingFace model: {self.settings.huggingface_model}")
                self._tokenizer = AutoTokenizer.from_pretrained(
                    self.settings.huggingface_model
                )
                self._model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.settings.huggingface_model
                )
                print("Model loaded successfully!")
            except ImportError:
                raise ImportError(
                    "transformers library not installed. Install with: pip install transformers torch"
                )

    async def translate_text(
        self, text: str, source_lang: str = "EN", target_lang: str = "ZH"
    ) -> Dict[str, Any]:
        """Translate text using HuggingFace model"""
        try:
            if not text.strip():
                return {"success": False, "error": "No text provided for translation"}

            # Detect source language if not provided
            if not source_lang:
                source_lang = self._detect_language(text)

            # Check if translation is needed
            if source_lang == target_lang:
                return {
                    "success": True,
                    "translated_text": text,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                }

            # Load model if not loaded
            self._load_model()

            # Split text into chunks if it's too long
            chunks = self._chunk_text(text, self.max_chunk_size)

            if len(chunks) == 1:
                # Single chunk translation
                result = await self._translate_single_chunk(chunks[0])
            else:
                # Multiple chunks translation
                result = await self._translate_multiple_chunks(chunks)

            result["source_lang"] = source_lang
            result["target_lang"] = target_lang
            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"HuggingFace translation failed: {str(e)}",
            }

    async def _translate_single_chunk(self, text: str) -> Dict[str, Any]:
        """Translate a single chunk of text"""
        try:
            # Run synchronous translation in thread pool
            translated_text = await asyncio.get_event_loop().run_in_executor(
                None, self._translate_text_sync, text
            )

            return {
                "success": True,
                "translated_text": translated_text,
                "chunks_translated": 1,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Single chunk translation failed: {str(e)}",
            }

    async def _translate_multiple_chunks(self, chunks: List[str]) -> Dict[str, Any]:
        """Translate multiple chunks of text"""
        try:
            translated_chunks = []

            for chunk in chunks:
                # Run synchronous translation in thread pool
                translated_text = await asyncio.get_event_loop().run_in_executor(
                    None, self._translate_text_sync, chunk
                )
                translated_chunks.append(translated_text)

                # Add small delay to prevent overload
                await asyncio.sleep(0.05)

            return {
                "success": True,
                "translated_text": " ".join(translated_chunks),
                "chunks_translated": len(chunks),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Multiple chunk translation failed: {str(e)}",
            }

    def _translate_text_sync(self, text: str) -> str:
        """Synchronous translation using the loaded model"""
        # Tokenize input
        inputs = self._tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=512
        )

        # Generate translation
        with self._model.no_grad():
            outputs = self._model.generate(
                **inputs, max_length=512, num_beams=4, early_stopping=True
            )

        # Decode output
        translated_text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translated_text


class DeepLTranslator(BaseTranslator):
    """DeepL Translator using API (requires API key, high quality)"""

    def __init__(self, settings: Settings):
        super().__init__(settings)
        if not settings.deepl_api_key:
            raise ValueError("DeepL API key is required for DeepL translation")
        self.api_key = settings.deepl_api_key

    async def translate_text(
        self, text: str, source_lang: str = "EN", target_lang: str = "ZH"
    ) -> Dict[str, Any]:
        """Translate text using DeepL API"""
        try:
            import deepl

            if not text.strip():
                return {"success": False, "error": "No text provided for translation"}

            # Detect source language if not provided
            if not source_lang:
                source_lang = self._detect_language(text)

            # Check if translation is needed
            if source_lang == target_lang:
                return {
                    "success": True,
                    "translated_text": text,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                }

            # Split text into chunks if it's too long
            chunks = self._chunk_text(text, self.max_chunk_size)

            if len(chunks) == 1:
                # Single chunk translation
                result = await self._translate_single_chunk(
                    chunks[0], source_lang, target_lang
                )
            else:
                # Multiple chunks translation
                result = await self._translate_multiple_chunks(
                    chunks, source_lang, target_lang
                )

            return result

        except Exception as e:
            return {"success": False, "error": f"DeepL translation failed: {str(e)}"}

    async def _translate_single_chunk(
        self, text: str, source_lang: str, target_lang: str
    ) -> Dict[str, Any]:
        """Translate a single chunk of text"""
        try:
            import deepl

            translator = deepl.Translator(self.api_key)

            # Run synchronous translation in thread pool
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: translator.translate_text(
                    text, source_lang=source_lang, target_lang=target_lang
                ),
            )

            return {
                "success": True,
                "translated_text": result.text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "chunks_translated": 1,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Single chunk translation failed: {str(e)}",
            }

    async def _translate_multiple_chunks(
        self, chunks: List[str], source_lang: str, target_lang: str
    ) -> Dict[str, Any]:
        """Translate multiple chunks of text"""
        try:
            import deepl

            translator = deepl.Translator(self.api_key)
            translated_chunks = []

            for chunk in chunks:
                # Run synchronous translation in thread pool
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda c=chunk: translator.translate_text(
                        c, source_lang=source_lang, target_lang=target_lang
                    ),
                )
                translated_chunks.append(result.text)

                # Add small delay to respect rate limits
                await asyncio.sleep(0.1)

            return {
                "success": True,
                "translated_text": " ".join(translated_chunks),
                "source_lang": source_lang,
                "target_lang": target_lang,
                "chunks_translated": len(chunks),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Multiple chunk translation failed: {str(e)}",
            }

class OpenAITranslator(BaseTranslator):
    """OpenAI API Translator using API (requires translator_api_key, translator_api_base, translator_api_model)"""

    def __init__(self, settings: Settings):
        super().__init__(settings)
        if not settings.translator_api_key:
            raise ValueError("Translator API key is required for Translator translation")
        if not settings.translator_api_base:
            raise ValueError("Translator API base URL is required for Translator translation")
        if not settings.translator_api_model:
            raise ValueError("Translator API model is required for Translator translation")
        self.api_key = settings.translator_api_key
        self.api_base = settings.translator_api_base
        self.api_model = settings.translator_api_model
        self.model = init_translator_model(
            self.api_key, self.api_base, self.api_model
        )
        self.default_prompt = DEFAULT_TRANSLATOR_PROMPT

    async def translate_text(
        self, text: str, source_lang: str = "EN", target_lang: str = "ZH"
    ) -> Dict[str, Any]:
        """Translate text using OpenAI API Translator API"""
        try:
            if not text.strip():
                return {"success": False, "error": "No text provided for translation"}

            # Detect source language if not provided
            if not source_lang:
                source_lang = self._detect_language(text)

            # Check if translation is needed
            if source_lang == target_lang:
                return {
                    "success": True,
                    "translated_text": text,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                }

            # Split text into chunks if it's too long
            chunks = self._chunk_text(text, self.max_chunk_size)

            if len(chunks) == 1:
                # Single chunk translation
                result = await self._translate_single_chunk(
                    chunks[0], source_lang, target_lang
                )
            else:
                # Multiple chunks translation
                result = await self._translate_multiple_chunks(
                    chunks, source_lang, target_lang
                )

            return result

        except Exception as e:
            return {"success": False, "error": f"OpenAI API Translator translation failed: {str(e)}"}

    async def _translate_single_chunk(
        self, text: str, source_lang: str, target_lang: str
    ) -> Dict[str, Any]:
        """Translate a single chunk of text"""
        try:
            prompt = self.default_prompt.format(
                source_lang=source_lang, target_lang=target_lang, input_text=text
            )

            # Run synchronous translation in thread pool
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.invoke(prompt),
            )

            return {
                "success": True,
                "translated_text": result.content,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "chunks_translated": 1,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Single chunk translation failed: {str(e)}",
            }

    async def _translate_multiple_chunks(
        self, chunks: List[str], source_lang: str, target_lang: str
    ) -> Dict[str, Any]:
        """Translate multiple chunks of text"""
        try:
            translated_chunks = []

            for chunk in chunks:
                prompt = self.default_prompt.format(
                source_lang=source_lang, target_lang=target_lang, input_text=chunk
            )
                # Run synchronous translation in thread pool
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.model.invoke(prompt),
                )
                translated_chunks.append(result.content)

                # Add small delay to respect rate limits
                await asyncio.sleep(0.1)

            return {
                "success": True,
                "translated_text": " ".join(translated_chunks),
                "source_lang": source_lang,
                "target_lang": target_lang,
                "chunks_translated": len(chunks),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Multiple chunk translation failed: {str(e)}",
            }


def create_translator(settings: Settings) -> BaseTranslator:
    """Create translator instance based on settings"""
    if settings.translation_engine == "deepl":
        if not settings.use_deepl:
            raise ValueError(
                "DeepL API key is required for DeepL translation. Configure DEEPL_API_KEY in .env or use a different engine."
            )
        return DeepLTranslator(settings)
    elif settings.translation_engine == "googletrans":
        return GoogleTranslator(settings)
    elif settings.translation_engine == "huggingface":
        return HuggingFaceTranslator(settings)
    elif settings.translation_engine == "openai":
        return OpenAITranslator(settings)
    else:
        raise ValueError(
            f"Unsupported translation engine: {settings.translation_engine}"
        )

# Backward compatibility
class Translator:
    """Backward compatibility wrapper"""

    def __init__(self, settings: Settings):
        self.translator = create_translator(settings)
        self.settings = settings

    async def translate_text(
        self, text: str, source_lang: str = "EN", target_lang: str = "ZH"
    ) -> Dict[str, Any]:
        """Translate text using the configured engine"""
        return await self.translator.translate_text(text, source_lang, target_lang)

    async def translate_document_content(
        self, content: str,  preserve_formatting: bool = True, source_lang: str = "EN", target_lang: str = "ZH"
    ) -> Dict[str, Any]:
        """Translate document content with optional formatting preservation"""
        if preserve_formatting:
            return await self._translate_with_formatting(content, source_lang, target_lang)
        else:
            return await self.translate_text(content, source_lang, target_lang)

    async def _translate_with_formatting(self, content: str, source_lang: str = "EN", target_lang: str = "ZH") -> Dict[str, Any]:
        """Translate content while preserving markdown formatting"""
        # Split content by markdown patterns
        lines = content.split("\n")
        translated_lines = []

        for line in lines:
            # Check if it's a markdown header
            if line.startswith("#"):
                # Translate header content
                header_level = len(line) - len(line.lstrip("#"))
                header_text = line.lstrip("#").strip()

                if header_text:
                    translation = await self.translate_text(header_text, source_lang, target_lang)
                    if translation["success"]:
                        translated_line = (
                            "#" * header_level + " " + translation["translated_text"]
                        )
                    else:
                        translated_line = line
                else:
                    translated_line = line
            elif line.startswith("!["):
                # Preserve images without translation
                translated_line = line
            elif line.strip() == "":
                # Preserve empty lines
                translated_line = line
            else:
                # Regular text
                translation = await self.translate_text(line, source_lang, target_lang)
                if translation["success"]:
                    translated_line = translation["translated_text"]
                else:
                    translated_line = line

            translated_lines.append(translated_line)

        return {
            "success": True,
            "translated_text": "\n".join(translated_lines),
            "formatting_preserved": True,
        }

# 翻译markdown文件，保留格式
def translate_markdown(input_path: str, output_path: str="./", settings: Settings = None, source_lang: str = "EN", target_lang: str = "ZH") -> str:
    """Translate markdown content while preserving formatting"""
    # 读取输入markdown文件
    with open(input_path, 'r', encoding='utf-8') as f:
        markdown = f.read()
    
    if not settings:
        settings = Settings()
    translator = Translator(settings)
    result = asyncio.run(translator.translate_document_content(markdown, True, source_lang, target_lang))

    # 检查输出文件是否存在,准备写入
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
    file_name = os.path.basename(input_path).replace('.md', f'_{target_lang}.md')
    # 写入翻译后的markdown文件
    with open(os.path.join(output_path, file_name), 'w', encoding='utf-8') as f:
        f.write(result["translated_text"])

    return result["translated_text"]

# 翻译文本内容
def translate_text(input_path: str, output_path: str="./", settings: Settings = None, source_lang: str = "EN", target_lang: str = "ZH") -> str:
    """Translate text content while not preserving formatting"""
    # 读取输入文本文件
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    if not settings:
        settings = Settings()
    translator = Translator(settings)
    result = asyncio.run(translator.translate_text(text, source_lang, target_lang))

    # 检查输出文件是否存在,准备写入
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
    
    file_name = os.path.basename(input_path).split('.')[0] + f'_{target_lang}.md'
    # 写入翻译后的文本文件
    with open(os.path.join(output_path, file_name), 'w', encoding='utf-8') as f:
        f.write(result["translated_text"])

    return result["translated_text"]