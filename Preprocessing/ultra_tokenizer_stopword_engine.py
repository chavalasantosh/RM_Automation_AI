import spacy
import re
import unicodedata
import contractions
import textstat
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory
from typing import List, Union, Set, Dict, Any, cast, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

# Ensure langdetect produces consistent results
DetectorFactory.seed = 0

class UltraTokenizerStopwordEngine:
    """
    An ultra-advanced, multilingual, and domain-aware text processing engine
    for tokenization, stopword removal, and text analysis.
    """

    # Mapping of common language codes to spaCy model names
    LANG_MODEL_MAP = {
        'en': 'en_core_web_sm',
        'es': 'es_core_news_sm',
        'fr': 'fr_core_news_sm',
        'de': 'de_core_news_sm',
        'it': 'it_core_news_sm',
        'pt': 'pt_core_news_sm',
        'nl': 'nl_core_news_sm',
        'ru': 'ru_core_news_sm',
        'zh': 'zh_core_web_sm',
        'ja': 'ja_core_news_sm',
        'ar': 'ar_core_web_sm',
        # Add more as needed
    }

    def __init__(self, default_model: str = 'en_core_web_sm', domain_keywords: Optional[Dict[str, List[str]]] = None, **kwargs):
        """
        Initializes the UltraTokenizerStopwordEngine with a spaCy model and various
        text processing options.

        Args:
            default_model (str): The default spaCy language model to use if auto-detection fails.
            domain_keywords (Dict[str, List[str]]): A dictionary mapping domain names to lists of keywords.
            **kwargs: Additional flags for processing behavior.
                      expand_contractions (bool): Expand contractions (e.g., "don't" -> "do not").
                      remove_html (bool): Remove HTML tags from text.
                      remove_emojis (bool): Remove emoji characters.
                      remove_accented_chars (bool): Transliterate accented chars to ASCII.
                      remove_punctuation (bool): Remove punctuation.
                      remove_numbers (bool): Remove numbers.
                      remove_urls (bool): Remove URLs.
                      remove_emails (bool): Remove email addresses.
                      lemmatize (bool): Perform lemmatization.
                      remove_entities (bool): Remove named entities.
                      remove_stopwords (bool): Remove standard stopwords.
                      custom_stopwords (Set[str]): A set of custom stopwords to add.
                      preserve_acronyms (bool): Prevent acronyms from being lowercased/lemmatized.
        """
        self.options = {
            'expand_contractions': kwargs.get('expand_contractions', True),
            'remove_html': kwargs.get('remove_html', True),
            'remove_emojis': kwargs.get('remove_emojis', True),
            'remove_accented_chars': kwargs.get('remove_accented_chars', True),
            'remove_punctuation': kwargs.get('remove_punctuation', True),
            'remove_numbers': kwargs.get('remove_numbers', True),
            'remove_urls': kwargs.get('remove_urls', True),
            'remove_emails': kwargs.get('remove_emails', True),
            'lemmatize': kwargs.get('lemmatize', True),
            'remove_entities': kwargs.get('remove_entities', False),
            'remove_stopwords': kwargs.get('remove_stopwords', True),
            'preserve_acronyms': kwargs.get('preserve_acronyms', False),
        }
        
        self.emoji_pattern = re.compile(
            "["
            "😀-🙏"  # emoticons
            "🌀-🗿"  # symbols & pictographs
            "🚀-🛿"  # transport & map symbols
            "🜀-🝿"  # alchemical symbols
            "🞀-🟿"  # Geometric Shapes Extended
            "🠀-🣿"  # Supplemental Arrows-C
            "🤀-🧿"  # Supplemental Symbols and Pictographs
            "🨀-🩯"  # Chess Symbols
            "🩰-🫿"  # Symbols and Pictographs Extended-A
            "✂-➰"  # Dingbats
            "Ⓜ-🉑" 
            "]+",
            flags=re.UNICODE,
        )
        
        # Regex for character flooding (e.g., 'sooooo')
        self.char_flood_pattern = re.compile(r'(.)\\1{2,}')
        
        self.default_model = default_model
        self.domain_keywords = domain_keywords if domain_keywords is not None else self._get_default_domain_keywords()
        self.nlp = self._load_spacy_model(default_model) # Load default model initially

        # Initialize sentence transformer model for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        if kwargs.get('custom_stopwords'):
            self.add_stopwords(kwargs['custom_stopwords'])

    def _get_default_domain_keywords(self) -> Dict[str, List[str]]:
        return {
            "finance": ["stock", "bond", "market", "invest", "economy", "financial", "revenue", "profit", "loss", "dividend"],
            "legal": ["law", "court", "act", "statute", "case", "judgment", "contract", "agreement", "legal", "jurisdiction"],
            "medical": ["patient", "disease", "drug", "therapy", "diagnosis", "symptom", "health", "medical", "clinic", "hospital"],
            "tech": ["software", "hardware", "algorithm", "data", "network", "cyber", "AI", "machine learning", "cloud", "programming"],
            "conversational": ["hello", "hi", "how are you", "what's up", "talk", "chat", "said", "asked"],
            "code": ["def", "class", "import", "function", "var", "const", "return", "print", "console.log", "{", "}", "<", ">", "/", "="],
        }

    def _load_spacy_model(self, model_name: str):
        """Loads a spaCy model, handling missing models."""
        try:
            nlp = spacy.load(model_name)
            if 'parser' in nlp.pipe_names and 'parser' not in nlp.pipe_names: # Keep parser if it's explicitly enabled by default
                nlp.disable_pipes('parser')
            if 'ner' in nlp.pipe_names and not self.options['remove_entities']:
                nlp.disable_pipes('ner')

            if 'sentencizer' not in nlp.pipe_names:
                nlp.add_pipe("sentencizer")
            return nlp
        except OSError:
            print(f"SpaCy model '{model_name}' not found. Please download it by running: python -m spacy download {model_name}")
            raise # Re-raise the OSError to indicate the model is missing

    def _normalize_text(self, text: str) -> str:
        """Internal method to run sequential normalization steps."""
        if self.options['remove_html']:
            text = BeautifulSoup(text, "html.parser").get_text()
        if self.options['expand_contractions']:
            text = contractions.fix(text) # type: ignore
        if self.options['remove_emojis']:
            text = self.emoji_pattern.sub(r'', text)
        if self.options['remove_accented_chars']:
            text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        
        # Handle character flooding (e.g., 'sooooo' -> 'soo')
        text = self.char_flood_pattern.sub(r'\\1\\1', text)
        
        # Normalize multiple spaces to single space
        text = re.sub(r'\\s+', ' ', text).strip()
        
        return text

    def detect_language(self, text: str) -> str:
        """Detects the language of the input text and attempts to load the corresponding spaCy model."""
        try:
            lang = cast(str, detect(text)) # type: ignore
            # Attempt to load a new model if the language changes and a model is available
            if lang != self.nlp.lang and lang in self.LANG_MODEL_MAP:
                try:
                    self.nlp = self._load_spacy_model(self.LANG_MODEL_MAP[lang])
                    print(f"Dynamically loaded spaCy model for language: {lang}")
                except Exception as e:
                    print(f"Could not load spaCy model for {lang}: {e}. Sticking with current model.")
            return lang
        except:
            return 'unknown'

    def _detect_domain(self, text: str) -> str:
        """Basic keyword-based domain detection."""
        text_lower = text.lower()
        scores = {domain: 0 for domain in self.domain_keywords}

        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    scores[domain] += 1
        
        if not any(scores.values()):
            return "general"
        
        return max(scores, key=scores.get) # type: ignore

    def tokenize(self, text: str, return_tokens: bool = True) -> Union[str, List[str]]:
        """
        Processes text through normalization and tokenization pipeline.

        Args:
            text (str): The input text.
            return_tokens (bool): If True, returns a list of tokens. Otherwise, a joined string.

        Returns:
            Union[str, List[str]]: Processed text as a string or list of tokens.
        """
        if not isinstance(text, str) or not text.strip():
            return [] if return_tokens else ""

        # First, detect language and potentially switch spaCy model
        self.detect_language(text) # This updates self.nlp internally

        normalized_text = self._normalize_text(text)
        doc = self.nlp(normalized_text)
        
        processed_tokens = []
        for token in doc:
            if self.options['remove_urls'] and token.like_url:
                continue
            if self.options['remove_emails'] and token.like_email:
                continue
            if self.options['remove_numbers'] and (token.is_digit or token.like_num):
                continue
            if self.options['remove_punctuation'] and token.is_punct:
                continue
            if self.options['remove_stopwords'] and token.is_stop:
                continue
            if self.options['remove_entities'] and token.ent_type_:
                continue
            if token.is_space:
                continue

            processed_token = token.lemma_.lower().strip() if self.options['lemmatize'] else token.text.lower().strip()
            
            # Prevent lowercasing/lemmatization for certain tokens if remove_entities is False
            if not self.options['remove_entities']:
                if token.is_currency or (token.like_num and '%' in token.text):
                    processed_token = token.text.strip() # Keep original text for currency/percentage
                elif self.options.get('preserve_acronyms', False) and token.is_upper and len(token.text) > 1 and token.text.isalpha():
                    processed_token = token.text.strip() # Preserve original casing for acronyms

            if processed_token:
                processed_tokens.append(processed_token)

        return processed_tokens if return_tokens else ' '.join(processed_tokens)

    def remove_stopwords(self, text: str) -> str:
        """
        Removes stopwords from the text based on the engine's configuration.
        """
        original_remove_stopwords_setting = self.options['remove_stopwords']
        self.options['remove_stopwords'] = True
        processed_text = cast(str, self.tokenize(text, return_tokens=False))
        self.options['remove_stopwords'] = original_remove_stopwords_setting # Restore setting
        return processed_text

    def auto_generate_stopwords(self, corpus: List[str], top_n: int = 100) -> Set[str]:
        """
        Generates custom stopwords based on token frequency from a given corpus.
        This is a simplified version and does not use entropy/TF-IDF.
        """
        all_tokens = []
        for text in corpus:
            all_tokens.extend(self.tokenize(text, return_tokens=True))
        
        from collections import Counter
        token_counts = Counter(all_tokens)
        
        current_stopwords = self.nlp.Defaults.stop_words
        
        candidate_stopwords = []
        for token, count in token_counts.most_common():
            if token.isalpha() and len(token) > 1 and token not in current_stopwords:
                candidate_stopwords.append(token)
            if len(candidate_stopwords) >= top_n:
                break
        
        return set(candidate_stopwords)

    def auto_generate_stopwords_tfidf(self, corpus: List[str], top_n: int = 100, min_df: float = 0.01, max_df: float = 0.95) -> Set[str]:
        """
        Generates custom stopwords based on TF-IDF scores from a given corpus.
        Words with high frequency (common) but low TF-IDF (low importance/discriminative power)
        are considered good candidates for stopwords.

        Args:
            corpus (List[str]): A list of documents (strings) to analyze.
            top_n (int): The number of top least discriminative words to suggest as stopwords.
            min_df (float): When building the vocabulary, ignore terms that have a document frequency
                            strictly lower than the given threshold (corpus-specific).
            max_df (float): When building the vocabulary, ignore terms that have a document frequency
                            strictly higher than the given threshold (common words across all documents).

        Returns:
            Set[str]: A set of auto-generated custom stopwords.
        """
        if not corpus:
            return set()

        # Tokenize the corpus first for TF-IDF calculation
        tokenized_corpus = [self.tokenize(doc, return_tokens=False) for doc in corpus]
        
        # Initialize TfidfVectorizer
        # We use a custom tokenizer that simply splits on space, as our tokenize method already handles complex tokenization
        vectorizer = TfidfVectorizer(min_df=min_df, max_df=max_df, stop_words='english') # Use default English stopwords as a base
        
        try:
            tfidf_matrix = vectorizer.fit_transform(tokenized_corpus)
            feature_names = vectorizer.get_feature_names_out()

            # Calculate inverse document frequency (IDF) as a measure of a word's rarity
            # Lower IDF means more common across documents
            idf_scores = vectorizer.idf_
            
            # Create a list of (word, idf_score) tuples
            word_idf_scores = sorted(list(zip(feature_names, idf_scores)), key=lambda x: x[1])

            # Select the top_n words with the lowest IDF scores as potential stopwords
            # These are the most common words that are least unique to any specific document
            custom_stopwords = set()
            current_spacy_stopwords = self.nlp.Defaults.stop_words
            
            for word, score in word_idf_scores:
                # Ensure the word is not already a spaCy stopword and is alphabetic (filter out noise)
                if word.isalpha() and word not in current_spacy_stopwords:
                    custom_stopwords.add(word)
                if len(custom_stopwords) >= top_n:
                    break
            return custom_stopwords
        except ValueError as e:
            print(f"Error generating TF-IDF stopwords: {e}. Returning empty set.")
            return set()

    def _calculate_semantic_embedding(self, text: str) -> List[float]:
        """
        Placeholder for calculating a semantic embedding for a text.
        In a full implementation, this would involve using a pre-trained
        language model to get embeddings.
        For now, it returns a simple hash or None.
        """
        # This would require a pre-trained transformer model (e.g., Sentence-BERT)
        # For demonstration, we'll return a simple hash or None
        embedding = self.embedding_model.encode(text).tolist()
        return embedding

    def get_token_metadata(self, text: str) -> List[Dict[str, Any]]:
        """
        Returns rich metadata for each token in the processed text.
        """
        if not isinstance(text, str) or not text.strip():
            return []

        # Ensure the correct language model is loaded before processing for metadata
        detected_lang = self.detect_language(text)
        detected_domain = self._detect_domain(text)

        normalized_text = self._normalize_text(text)
        doc = self.nlp(normalized_text)
        
        metadata_list = []
        for token in doc:
            # Basic check for code-like tokens (can be expanded)
            is_code_token = bool(re.search(r'''[{}()<>\[\]\\=;:,."'']|\\b(def|class|import|return|console.log)\\b''', token.text)) # type: ignore

            token_meta = {
                "text": token.text,
                "lemma": token.lemma_,
                "pos": token.pos_,
                "is_stop": token.is_stop,
                "is_punct": token.is_punct,
                "is_digit": token.is_digit,
                "like_url": token.like_url,
                "like_email": token.like_email,
                "entity_type": token.ent_type_ if token.ent_type_ else None,
                "lang": detected_lang, # Use the detected language for the whole document
                "domain": detected_domain, # Add detected domain
                "is_alpha": token.is_alpha,
                "is_lower": token.is_lower,
                "is_upper": token.is_upper,
                "is_title": token.is_title,
                "is_currency": token.is_currency, # spaCy attribute for currency symbols
                "is_percent": token.like_num and '%' in token.text, # Custom check for percentages
                "is_code": is_code_token,
                "semantic_embedding": self._calculate_semantic_embedding(token.text), # Call the actual embedding method
            }
            metadata_list.append(token_meta)
        return metadata_list

    def segment_sentences(self, text: str, clean: bool = False) -> List[str]:
        """
        Segments text into sentences.
        """
        if not isinstance(text, str) or not text.strip():
            return []

        # Ensure the correct language model is loaded before processing
        self.detect_language(text)

        doc = self.nlp(text)
        if clean:
            return [" ".join(sent.text.split()).strip() for sent in doc.sents]
        return [sent.text.strip() for sent in doc.sents]

    def segment_paragraphs(self, text: str, clean: bool = False) -> List[str]:
        """
        Segments text into paragraphs based on multiple newline characters.
        Args:
            text (str): The input text.
            clean (bool): If True, also cleans each paragraph by trimming whitespace.
        Returns:
            List[str]: A list of paragraphs.
        """
        if not isinstance(text, str) or not text.strip():
            return []

        paragraphs = re.split(r'\n\s*\n+', text.strip())
        if clean:
            return [p.strip() for p in paragraphs if p.strip()]
        return [p for p in paragraphs if p.strip()]
        
    def get_readability_scores(self, text: str) -> Dict[str, float]:
        """
        Calculates various readability scores for the text using textstat.
        
        Returns:
            A dictionary containing different readability metrics.
        """
        if not isinstance(text, str) or not text.strip():
            return {
                'flesch_reading_ease': 0.0, 'flesch_kincaid_grade': 0.0,
                'gunning_fog': 0.0, 'smog_index': 0.0,
                'automated_readability_index': 0.0, 'coleman_liau_index': 0.0,
            }
        
        return {
            'flesch_reading_ease': textstat.flesch_reading_ease(text), # type: ignore
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text), # type: ignore
            'gunning_fog': textstat.gunning_fog(text), # type: ignore
            'smog_index': textstat.smog_index(text), # type: ignore
            'automated_readability_index': textstat.automated_readability_index(text), # type: ignore
            'coleman_liau_index': textstat.coleman_liau_index(text), # type: ignore
        }

    def add_stopwords(self, words: Set[str]):
        """Adds custom words to the stopword list."""
        for word in words:
            self.nlp.vocab[word].is_stop = True

# --- Example Usage ---
if __name__ == "__main__":
    sample_text_en = """
    <p>Hello there! I'm an <b>advanced</b> user & I wouldn't say this is easy. 🤔</p>
    <p>My contact is advanced.user@example.com. Check our résumé at https://example.com/cv.</p>
    <p>This is a test of crème brûlée. We're running tests in 2024. What a wonderful day! 😃</p>
    Sooooo good!!! This is some { "json": "data" } and <code>import os</code> and $100.00.
    """
    
    sample_text_es = """
    Hola, ¿cómo estás? Soy un usuario avanzado y esto no es fácil. Me puedes contactar en contacto@ejemplo.com.
    Visita nuestro sitio web en https://ejemplo.com/es. Este es un ejemplo legal para un contrato importante.
    """

    print("--- UltraTokenizerStopwordEngine Example (English) ---")
    
    # Initialize the engine for English with custom domain keywords
    custom_domains = {
        "tech_domain": ["api", "algorithm", "software", "import", "json"],
        "food_domain": ["crème brûlée", "pizza", "recipe"]
    }
    engine_en = UltraTokenizerStopwordEngine(default_model='en_core_web_sm', domain_keywords=custom_domains, remove_entities=True)
    
    print("\nOriginal English Text:\n", sample_text_en)
    
    # Test tokenize
    tokenized_text_en = engine_en.tokenize(sample_text_en)
    print("\nTokenized English Text (list):\n", tokenized_text_en)
    print("\nTokenized English Text (joined string):\n", " ".join(tokenized_text_en))

    # Test get_token_metadata
    metadata_en = engine_en.get_token_metadata(sample_text_en)
    print("\nEnglish Token Metadata (first 10 tokens):\n", metadata_en[:10])
    
    # Test segment_sentences
    sentences_en = engine_en.segment_sentences(sample_text_en, clean=True)
    print("\nEnglish Sentences:\n", sentences_en)

    # Test segment_paragraphs
    paragraphs_en = engine_en.segment_paragraphs(sample_text_en, clean=True)
    print("\nEnglish Paragraphs:\n", paragraphs_en)
    
    # Test detect_language and domain for English
    lang_en = engine_en.detect_language(sample_text_en)
    domain_en = engine_en._detect_domain(sample_text_en)
    print(f"\nDetected English Language: {lang_en}")
    print(f"Detected English Domain: {domain_en}")

    print("\n--- UltraTokenizerStopwordEngine Example (Spanish) ---")
    
    # Initialize a new engine for Spanish (or it will dynamically load)
    engine_es = UltraTokenizerStopwordEngine(default_model='es_core_news_sm')

    print("\nOriginal Spanish Text:\n", sample_text_es)

    # Test tokenize (should dynamically load Spanish model)
    tokenized_text_es = engine_es.tokenize(sample_text_es)
    print("\nTokenized Spanish Text (list):\n", tokenized_text_es)
    print("\nTokenized Spanish Text (joined string):\n", " ".join(tokenized_text_es))

    # Test get_token_metadata for Spanish
    metadata_es = engine_es.get_token_metadata(sample_text_es)
    print("\nSpanish Token Metadata (first 5 tokens):\n", metadata_es[:5])

    # Test detect_language and domain for Spanish
    lang_es = engine_es.detect_language(sample_text_es)
    domain_es = engine_es._detect_domain(sample_text_es)
    print(f"\nDetected Spanish Language: {lang_es}")
    print(f"Detected Spanish Domain: {domain_es}")

    print("\n--- Readability Analysis ---")
    readable_text_for_scores = (
        "SpaCy is an open-source software library for advanced Natural Language Processing, "
        "written in the programming languages Python and Cython. The library is published under the MIT license."
    )
    readability_scores = engine_en.get_readability_scores(readable_text_for_scores)
    print("\nReadability Scores (English):\n", readability_scores)

    print("\n--- Auto-generated Stopwords ---")
    corpus_for_stopwords = [
        "This is a sample document about natural language processing.",
        "Another document with common words and some unique terms.",
        "NLP is a fascinating field."
    ]
    custom_generated_stopwords = engine_en.auto_generate_stopwords(corpus_for_stopwords, top_n=5)
    print(f"\nAuto-generated Custom Stopwords (top 5): {custom_generated_stopwords}")

    # Test auto_generate_stopwords_tfidf
    corpus_for_tfidf_stopwords = [
        "The quick brown fox jumps over the lazy dog. The dog is very lazy.",
        "A quick brown cat runs fast. The cat is not lazy.",
        "Dogs and cats are common pets. They are very popular.",
        "This is a document about machine learning. Machine learning is a field of artificial intelligence."
    ]
    tfidf_generated_stopwords = engine_en.auto_generate_stopwords_tfidf(corpus_for_tfidf_stopwords, top_n=5)
    print(f"\nTF-IDF Generated Custom Stopwords (top 5): {tfidf_generated_stopwords}")

    # Test with preserved entities and acronyms
    print("\n--- Testing Entity and Acronym Preservation ---")
    entity_acronym_text = "Google (GOOG) announced a 10% increase in revenue for Q3 2024. The CEO praised the R&D team."
    engine_preserve = UltraTokenizerStopwordEngine(default_model='en_core_web_sm', remove_entities=False, preserve_acronyms=True, lemmatize=False, remove_stopwords=False)
    
    print("\nOriginal Text (Entity/Acronym Test):\n", entity_acronym_text)
    tokenized_preserve = engine_preserve.tokenize(entity_acronym_text)
    print("\nTokenized (Entities/Acronyms Preserved):\n", tokenized_preserve)
    metadata_preserve = engine_preserve.get_token_metadata(entity_acronym_text)
    print("\nMetadata (Entities/Acronyms Preserved - first 15 tokens):\n", metadata_preserve[:15])

    # Demonstrate adding custom stopwords
    engine_en.add_stopwords({"sample", "document"})
    print("\nText after adding custom stopwords 'sample', 'document':\n", 
          engine_en.tokenize(corpus_for_stopwords[0], return_tokens=False))

    print("\n--- Testing Semantic Embedding ---")
    embedding_text = "Natural Language Processing is a fascinating field."
    embedding_engine = UltraTokenizerStopwordEngine(default_model='en_core_web_sm')
    embedding = embedding_engine._calculate_semantic_embedding(embedding_text)
    print(f"\nText: '{embedding_text}'")
    print(f"Semantic Embedding (first 5 elements): {embedding[:5]}...")
    print(f"Embedding Dimension: {len(embedding)}")

    # Test token metadata with embeddings
    metadata_with_embeddings = embedding_engine.get_token_metadata("The quick brown fox.")
    print("\nToken Metadata with Semantic Embeddings (first token):")
    import pprint
    pprint.pprint(metadata_with_embeddings[0]) 