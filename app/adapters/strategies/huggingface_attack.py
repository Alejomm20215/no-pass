"""Hugging Face AI-powered password attack strategy (Local Model)"""

import json
import os
from pathlib import Path
from typing import Optional, Callable, List
import time

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Transformers not available. Install with: pip install transformers torch")

from app.core.interfaces.attack_strategy import IAttackStrategy
from app.core.interfaces.pdf_handler import IPDFHandler
from app.core.domain.entities import CrackResult
from app.config.settings import settings


class HuggingFaceAIGenerator:
    """AI-powered password generator using local Hugging Face models"""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.AI_MODEL_NAME
        self.max_tokens = settings.AI_MAX_TOKENS
        self.temperature = settings.AI_TEMPERATURE
        self.generator = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        if TRANSFORMERS_AVAILABLE:
            try:
                # Use a lightweight text generation model
                self.generator = pipeline(
                    "text-generation",
                    model=self.model_name,
                    device=0 if self.device == "cuda" else -1,
                    model_kwargs={"torch_dtype": torch.float16 if self.device == "cuda" else None}
                )
            except Exception as e:
                print(f"Warning: Could not initialize local AI model: {e}")
                self.generator = None

    def generate_candidates(self, context: dict) -> List[str]:
        """Generate password candidates using local AI models"""
        if not self.generator:
            return self._fallback_generation(context)

        candidates = []

        # Extract contextual information
        filename = context.get('filename', '').lower()
        file_size = context.get('file_size', 0)
        creation_date = context.get('creation_date', '')

        # Generate candidates based on filename patterns
        filename_candidates = self._generate_from_filename_local(filename)
        candidates.extend(filename_candidates)

        # Generate candidates using local AI model
        ai_candidates = self._generate_with_local_ai(filename, creation_date)
        candidates.extend(ai_candidates)

        # Remove duplicates and limit
        candidates = list(set(candidates))[:50]  # Limit to 50 candidates

        return candidates

    def _generate_from_filename_local(self, filename: str) -> List[str]:
        """Generate candidates based on filename using pattern analysis"""
        candidates = []

        # Extract words from filename
        words = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ').split()

        # Generate contextual combinations
        for word in words:
            if len(word) >= 3:
                candidates.append(word)
                candidates.append(word.capitalize())
                if any(char.isdigit() for char in word):
                    # If word already has numbers, use it as-is
                    candidates.append(word)
                else:
                    # Add common number patterns
                    candidates.extend([
                        word + "123",
                        word + "2024",
                        word + "2023",
                        "123" + word,
                        word + "!",
                        word + "@"
                    ])

        # Common document type patterns
        if any(term in filename for term in ['report', 'invoice', 'contract']):
            candidates.extend(['company123', 'business2024', 'report2024', 'invoice2024'])
        if any(term in filename for term in ['personal', 'private', 'secret']):
            candidates.extend(['secret', 'private', 'personal', 'hidden'])

        return candidates

    def _generate_with_local_ai(self, filename: str, creation_date: str) -> List[str]:
        """Generate candidates using local AI models"""
        if not self.generator:
            return []

        try:
            # Create a prompt for password generation
            prompt = f"Generate 10 realistic passwords for a PDF file named '{filename}' created in {creation_date}. Make them varied with numbers and symbols:"

            # Generate text using the local model
            response = self.generator(
                prompt,
                max_length=self.max_tokens,
                temperature=self.temperature,
                num_return_sequences=1,
                do_sample=True,
                pad_token_id=self.generator.tokenizer.eos_token_id
            )

            # Parse the response to extract password-like strings
            generated_text = response[0]['generated_text'].strip()
            candidates = []

            # Simple parsing - look for alphanumeric strings with numbers/symbols
            import re
            password_pattern = r'\b[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]{6,20}\b'
            matches = re.findall(password_pattern, generated_text)

            for match in matches:
                if any(c.isdigit() for c in match) or any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in match):
                    candidates.append(match)

            return candidates[:10]  # Return top 10

        except Exception as e:
            print(f"Local AI generation failed: {e}")
            return []

    def _fallback_generation(self, context: dict) -> List[str]:
        """Fallback password generation when AI model is not available"""
        filename = context.get('filename', '').lower()

        candidates = [
            "password", "123456", "admin", "qwerty", "letmein",
            "welcome", "monkey", "password1", "123456789"
        ]

        # Add contextual candidates
        if 'report' in filename:
            candidates.extend(['report', 'company', 'business', 'report2024'])
        if 'invoice' in filename:
            candidates.extend(['invoice', 'payment', 'billing', 'invoice2024'])
        if 'contract' in filename:
            candidates.extend(['contract', 'agreement', 'legal', 'contract2024'])

        return candidates


class HuggingFaceAttack(IAttackStrategy):
    """AI-powered password attack strategy using Hugging Face models"""

    def __init__(self, pdf_handler: IPDFHandler, hf_generator: HuggingFaceAIGenerator):
        self.pdf_handler = pdf_handler
        self.hf_generator = hf_generator

    def execute(
        self,
        pdf_path: Path,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> CrackResult:
        """Execute Hugging Face AI-powered attack"""
        start_time = time.time()

        # Extract context from PDF
        context = self._extract_pdf_context(pdf_path)

        if progress_callback:
            progress_callback(10.0, "Analyzing PDF context with AI")

        # Generate AI-powered candidates
        hf_candidates = self.hf_generator.generate_candidates(context)

        if progress_callback:
            progress_callback(30.0, f"Generated {len(hf_candidates)} AI-powered password candidates")

        # Try AI-generated candidates first
        for idx, password in enumerate(hf_candidates, 1):
            if progress_callback:
                progress = 30.0 + (idx / len(hf_candidates)) * 50.0
                progress_callback(progress, f"Trying AI candidate: {password}")

            if self.pdf_handler.try_password(pdf_path, password):
                duration = time.time() - start_time
                return CrackResult(
                    success=True,
                    password=password,
                    method="ai_attack",
                    attempts=idx,
                    duration=duration
                )

        # If AI candidates fail, try fallback patterns
        if progress_callback:
            progress_callback(85.0, "AI candidates exhausted, trying fallback patterns")

        fallback_candidates = self.hf_generator._fallback_generation(context)

        for idx, password in enumerate(fallback_candidates, 1):
            if progress_callback:
                progress = 85.0 + (idx / len(fallback_candidates)) * 15.0
                progress_callback(progress, f"Trying fallback pattern: {password}")

            if self.pdf_handler.try_password(pdf_path, password):
                duration = time.time() - start_time
                return CrackResult(
                    success=True,
                    password=password,
                    method="ai_fallback",
                    attempts=len(hf_candidates) + idx,
                    duration=duration
                )

        # No password found
        duration = time.time() - start_time
        return CrackResult(
            success=False,
            method="ai_attack",
            attempts=len(hf_candidates) + len(fallback_candidates),
            duration=duration,
            error="No password found with AI assistance"
        )

    def _extract_pdf_context(self, pdf_path: Path) -> dict:
        """Extract contextual information from PDF"""
        context = {
            'filename': pdf_path.name,
            'file_size': pdf_path.stat().st_size,
            'creation_date': time.ctime(pdf_path.stat().st_mtime)
        }

        return context

    def estimate_time(self) -> float:
        """Estimate time for AI-powered attack"""
        # AI analysis + candidate testing (local model is faster than API)
        return 10.0 if self.hf_generator.generator else 5.0

    def estimate_attempts(self) -> int:
        """Estimate number of attempts"""
        return 30  # AI candidates + fallback patterns
