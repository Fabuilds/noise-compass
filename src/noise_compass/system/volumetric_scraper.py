
import re
import numpy as np
from typing import List, Dict, Any, Tuple

class VolumetricScraper:
    """
    Multi-Resolution Document Scrutiny Engine.
    Deconstructs documents into Character, Syllable, Word, and Sentence layers.
    Applies BitNet 1.58-bit ternary scoring to each resolution.
    """

    def __init__(self, resonance_engine=None):
        self.engine = resonance_engine # Likely the BitNetWorker or NeuralPrism
        self.vowels = 'aeiouy'

    def segment_syllables(self, word: str) -> List[str]:
        """
        Rule-based syllable segmentation (Acoustic Proxy).
        Uses vowel clusters as the core wave modulation points.
        """
        if not word: return []
        word = word.lower()
        # Heuristic: segments at vowel-consonant boundaries
        segments = []
        current = ""
        for i, char in enumerate(word):
            current += char
            if char in self.vowels:
                # If next char is a consonant followed by a vowel, segment here
                if i + 2 < len(word) and word[i+1] not in self.vowels and word[i+2] in self.vowels:
                    segments.append(current)
                    current = ""
        if current:
            segments.append(current)
        return segments

    def calculate_wave_modulation(self, scores: List[int]) -> float:
        """
        Measures the structural 'hum' or 'vibration' of a sequence.
        Calculates the mean absolute delta between contiguous ternary firings.
        """
        if len(scores) < 2: return 0.0
        deltas = [abs(scores[i] - scores[i-1]) for i in range(1, len(scores))]
        return float(np.mean(deltas))

    def scrutinize_document(self, text: str) -> Dict[str, Any]:
        """
        Executes the full multi-layered scrape.
        """
        # 1. Character Layer
        char_data = []
        for i, char in enumerate(text):
            # Proxying character score via BitNet Ternary Logic
            # In a real run, this calls self.engine.score_character(text, i)
            score = self._get_ternary_score(char) 
            char_data.append({"index": i, "char": char, "score": score})

        # 2. Syllable/Word Layer
        words = re.findall(r'\b\w+\b', text)
        word_data = []
        for word in words:
            syllables = self.segment_syllables(word)
            syllable_scores = [self._get_ternary_score(s) for s in syllables]
            modulation = self.calculate_wave_modulation(syllable_scores)
            
            word_data.append({
                "word": word,
                "syllables": syllables,
                "scores": syllable_scores,
                "modulation": modulation,
                "mean_score": float(np.mean(syllable_scores)) if syllable_scores else 0.0
            })

        # 3. Structural Evaluation (Sentences)
        sentences = re.split(r'[.!?]+', text)
        sentence_data = []
        for sent in sentences:
            if not sent.strip(): continue
            # Score at sentence level
            sentence_data.append({
                "text": sent.strip(),
                "score": self._get_ternary_score(sent)
            })

        return {
            "characters": char_data,
            "words": word_data,
            "sentences": sentence_data,
            "total_resonance": float(np.mean([c["score"] for c in char_data])) if char_data else 0.0
        }

    def _get_ternary_score(self, segment: str) -> int:
        """
        BitNet 1.58-bit Quantizer (Phase 130: Gap-Centric).
        Maps semantic resonance relative to Apophatic Gaps to {-1, 0, 1}.
        """
        if not self.engine or not hasattr(self.engine, 'dictionary'):
            # Fallback to random if engine is missing
            return int(np.random.choice([-1, 0, 1]))
            
        # Get apophatic metadata
        # We need an embedding for the segment
        from noise_compass.system.interference_engine import InterferenceEngine
        # Usually the engine has an embedder or prism
        if hasattr(self.engine, 'prism'):
            emb = self.engine.prism.embedder.embed(segment)
        else:
            # Last resort: mock embedding
            emb = np.random.randn(1024)

        gap_meta = self.engine.dictionary.apophatic_query(emb)
        tension = gap_meta.get("tension", 0.0)
        phase = gap_meta.get("phase", 0.0)
        
        # Phase 130 Scoring: 
        # 1  = High alignment with a boundary (Phase near 0 or pi/2? Wait.)
        # atan2(sim_r, sim_l):
        # 0      -> Pure Left Boundary
        # pi/2   -> Pure Right Boundary
        # pi/4   -> Void Center
        
        if phase < 0.3 or phase > 1.2:
            # Near a boundary ($0 \approx 0$ or $\pi/2 \approx 1.57$)
            return 1
        elif 0.6 < phase < 0.9:
            # Near the Center ($\pi/4 \approx 0.785$)
            return -1
        else:
            # Transition/Noise
            return 0
