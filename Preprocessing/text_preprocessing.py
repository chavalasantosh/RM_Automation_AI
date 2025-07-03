# Preprocessing/advanced_universal_text_preprocessor.py

import spacy
import re
from typing import List, Union, Set, Dict
from nltk.stem import PorterStemmer
# New imports for advanced features
from bs4 import BeautifulSoup
import unidecode
import contractions
import textstat

class AdvancedTextPreprocessor:
    """
    An advanced, universal text preprocessor using spaCy for robust, multilingual NLP tasks,
    enhanced with features for cleaning web content and analyzing text complexity.

    This class provides a comprehensive pipeline for text normalization and feature extraction.

    First, install required libraries:
    pip install spacy beautifulsoup4 unidecode contractions textstat
    
    Then, download a spaCy language model:
    python -m spacy download en_core_web_sm  # for English
    python -m spacy download es_core_news_sm  # for Spanish
    etc.
    """
    
    def __init__(self, 
                 model: str = 'en_core_web_sm',
                 expand_contractions: bool = True,
                 remove_html: bool = True,
                 remove_emojis: bool = True,
                 remove_accented_chars: bool = True,
                 remove_punctuation: bool = True,
                 remove_numbers: bool = True,
                 remove_urls: bool = True,
                 remove_emails: bool = True,
                 lemmatize: bool = True,
                 stem: bool = False,
                 remove_entities: bool = False,
                 remove_stopwords: bool = True,
                 custom_stopwords: Set[str] = None):
        """
        Initialize the advanced text preprocessor.
        
        Args:
            model (str): The spaCy language model to use.
            expand_contractions (bool): Expand contractions (e.g., "don't" -> "do not").
            remove_html (bool): Remove HTML tags from text.
            remove_emojis (bool): Remove emoji characters.
            remove_accented_chars (bool): Transliterate accented chars to ASCII.
            All other args are the same as the previous version.
        """
        # Basic cleaning flags
        self.expand_contractions = expand_contractions
        self.remove_html = remove_html
        self.remove_emojis = remove_emojis
        self.remove_accented_chars = remove_accented_chars
        self.remove_punctuation = remove_punctuation
        self.remove_numbers = remove_numbers
        self.remove_urls = remove_urls
        self.remove_emails = remove_emails
        
        # Token processing flags
        self.lemmatize = lemmatize
        self.stem = stem
        self.remove_entities = remove_entities
        self.remove_stopwords = remove_stopwords
        
        # Compile regex for emoji removal
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251" 
            "]+",
            flags=re.UNICODE,
        )
            
        if self.stem:
            self.lemmatize = False
            self.stemmer = PorterStemmer()
            
        try:
            # Disable components not strictly needed for the pipeline to speed up loading
            disable_pipes = ['parser']
            if not self.remove_entities and not self.get_sentences:
                disable_pipes.append('ner')
            self.nlp = spacy.load(model, disable=disable_pipes)
        except OSError:
            print(f"SpaCy model '{model}' not found. Please download it by running:\n"
                  f"python -m spacy download {model}")
            raise
        
        if custom_stopwords:
            self.add_stopwords(custom_stopwords)

    def _normalize_text(self, text: str) -> str:
        """Internal method to run sequential normalization steps."""
        if self.remove_html:
            text = BeautifulSoup(text, "html.parser").get_text()
        if self.expand_contractions:
            text = contractions.fix(text)
        if self.remove_emojis:
            text = self.emoji_pattern.sub(r'', text)
        if self.remove_accented_chars:
            text = unidecode.unidecode(text)
        return text

    def process_text(self, text: str, return_tokens: bool = False) -> Union[str, List[str]]:
        """
        Process text with all enabled preprocessing steps using the spaCy pipeline.
        
        Args:
            text (str): Input text to process.
            return_tokens (bool): Whether to return a list of tokens or a joined string.
            
        Returns:
            Processed text as a string or list of tokens.
        """
        if not isinstance(text, str):
            return [] if return_tokens else ""

        # Step 1: Run text normalization before tokenization
        normalized_text = self._normalize_text(text)
            
        # Step 2: Process the normalized text with spaCy
        doc = self.nlp(normalized_text)
        processed_tokens = []

        for token in doc:
            # Step 3: Filter tokens based on their attributes
            if self.remove_urls and token.like_url: continue
            if self.remove_emails and token.like_email: continue
            if self.remove_numbers and (token.is_digit or token.like_num): continue
            if self.remove_punctuation and token.is_punct: continue
            if self.remove_stopwords and token.is_stop: continue
            if self.remove_entities and token.ent_type_: continue
            if token.is_space: continue

            # Step 4: Perform lemmatization or stemming
            if self.lemmatize:
                processed_token = token.lemma_.lower().strip()
            elif self.stem:
                processed_token = self.stemmer.stem(token.text.lower()).strip()
            else:
                processed_token = token.text.lower().strip()
            
            if processed_token:
                processed_tokens.append(processed_token)
        
        return processed_tokens if return_tokens else ' '.join(processed_tokens)

    def get_readability_scores(self, text: str) -> Dict[str, float]:
        """
        Calculate various readability scores for the text.
        
        Returns:
            A dictionary containing different readability metrics.
        """
        return {
            'flesch_reading_ease': textstat.flesch_reading_ease(text),
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
            'gunning_fog': textstat.gunning_fog(text),
            'smog_index': textstat.smog_index(text),
            'automated_readability_index': textstat.automated_readability_index(text),
            'coleman_liau_index': textstat.coleman_liau_index(text),
        }

    # Helper methods (add/remove stopwords, get sentences, etc.) remain the same
    def add_stopwords(self, words: Set[str]):
        """Add custom words to the stopword list."""
        for word in words:
            self.nlp.vocab[word].is_stop = True

    def get_sentences(self, text: str, clean: bool = False) -> List[str]:
        """Split text into sentences."""
        doc = self.nlp(text)
        if clean:
            return [" ".join(sent.text.split()) for sent in doc.sents]
        return [sent.text for sent in doc.sents]
        
    def get_pos_tags(self, text: str) -> List[tuple]:
        """Get part-of-speech tags for each token."""
        doc = self.nlp(text)
        return [(token.text, token.pos_) for token in doc]
        
    def get_named_entities(self, text: str) -> List[tuple]:
        """Extract named entities from text."""
        if not self.nlp.has_pipe('ner'):
             # Load a new nlp object just for this, if needed
             temp_nlp = spacy.load(self.nlp.meta['name'])
             doc = temp_nlp(text)
        else:
            doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]

# --- Example Usage ---
if __name__ == "__main__":
    # A more complex example text with HTML, contractions, emojis, and accents
    advanced_sample_text = """
    <p>Hello there! I'm an <b>advanced</b> user & I wouldn't say this is easy. 🤔</p>
    <p>My contact is advanced.user@example.com. Check our résumé at https://example.com/cv.</p>
    <p>This is a test of crème brûlée. We're running tests in 2024. What a wonderful day! 😃</p>
    """
    
    print("--- Advanced Preprocessing (English) ---")
    # Initialize the advanced preprocessor with default settings
    adv_preprocessor = AdvancedTextPreprocessor(model='en_core_web_sm')
    
    # Process the text
    processed_text = adv_preprocessor.process_text(advanced_sample_text)
    print("\nOriginal Text:\n", advanced_sample_text)
    print("\nFully Processed Text:\n", processed_text)
    
    print("\n\n--- Readability Analysis ---")
    # Using a more standard text for readability scores
    readable_text = (
        "SpaCy is an open-source software library for advanced Natural Language Processing, "
        "written in the programming languages Python and Cython. The library is published under the MIT license."
    )
    scores = adv_preprocessor.get_readability_scores(readable_text)
    print("\nReadability of sample sentence:")
    for score_name, value in scores.items():
        print(f"- {score_name.replace('_', ' ').title()}: {value:.2f}")

    print("\n\n--- Extracting Entities from Complex Text ---")
    entities = adv_preprocessor.get_named_entities(advanced_sample_text)
    print("\nNamed Entities Found:\n", entities)
