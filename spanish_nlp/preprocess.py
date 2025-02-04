import re
import string

import emoji
from nltk.stem.snowball import SnowballStemmer

from spanish_nlp.utils.emo_unicode import demoticonize, emoticonize


class SpanishPreprocess:
    """Authors: Jorge Ortiz, Hernán Sarmiento, Ricardo Córdova"""

    def __init__(
        self,
        lower=True,
        remove_url=True,
        remove_hashtags=False,
        split_hashtags=True,
        normalize_breaklines=True,
        remove_emoticons=True,
        remove_emojis=True,
        convert_emoticons=False,
        convert_emojis=False,
        normalize_inclusive_language=False,
        reduce_spam=True,
        remove_vowels_accents=True,
        remove_multiple_spaces=True,
        remove_punctuation=True,
        remove_unprintable=True,
        remove_numbers=True,
        remove_stopwords=False,
        stopwords_list=None,
        lemmatize=False,
        stem=False,
        remove_html_tags=True,
        normalize_punctuation=False,
    ):
        """Spanish Preprocess Class for NLP tasks.

        Args:
            lower (bool, optional): convert text to lowercase. Defaults to True.
            remove_url (bool, optional): remove urls from text. Defaults to True.
            remove_hashtags (bool, optional): remove hashtags from text. Defaults to False.
            split_hashtags (bool, optional): split hashtags from text. Defaults to True.
            normalize_breaklines (bool, optional): remove multiple breaklines. Defaults to True.
            remove_emoticons (bool, optional): remove emoticons from text. Defaults to True.
            remove_emojis (bool, optional): remove emojis from text. Defaults to True.
            convert_emoticons (bool, optional): codify emoticons to text. Defaults to False.
            convert_emojis (bool, optional): codify emojis to text. Defaults to False.
            normalize_inclusive_language (bool, optional): normalize inclusive language. Defaults to False.
            reduce_spam (bool, optional): remove repeated words. Defaults to True.
            remove_vowels_accents (bool, optional): remove vowels with accents. Defaults to True.
            remove_multiple_spaces (bool, optional): remove multiple spaces. Defaults to True.
            remove_punctuation (bool, optional): remove punctuation. Defaults to True.
            remove_unprintable (bool, optional): remove unprintable characters. Defaults to True.
            remove_numbers (bool, optional): remove numbers. Defaults to True.
            remove_stopwords (bool, optional): remove stopwords. Defaults to False.
            stopwords_list (str, list, optional): stopwords name ('default', 'extended', 'nltk', 'spacy') or list of stopwords. Defaults to None.
            lemmatize (bool, optional): lemmatize text. Defaults to False.
            stem (bool, optional): stem text. Defaults to False.
            remove_html_tags (bool, optional): remove html tags. Defaults to True.
            normalize_punctuation (bool, optional): normalize punctuation. Defaults to False.
        """
        self.lower = lower
        self.remove_url = remove_url
        self.remove_hashtags = remove_hashtags
        self.split_hashtags = split_hashtags
        self.normalize_breaklines = normalize_breaklines
        self.remove_emojis = remove_emojis
        self.remove_emoticons = remove_emoticons
        self.convert_emoticons = convert_emoticons
        self.convert_emojis = convert_emojis
        self.normalize_inclusive_language = normalize_inclusive_language
        self.reduce_spam = reduce_spam
        self.remove_vowels_accents = remove_vowels_accents
        self.remove_multiple_spaces = remove_multiple_spaces
        self.remove_punctuation = remove_punctuation
        self.remove_numbers = remove_numbers
        self.remove_stopwords = remove_stopwords
        self._prepare_stopwords_(stopwords_list)
        self.remove_unprintable = remove_unprintable
        self.stem = stem
        self.lemmatize = lemmatize
        self.remove_html_tags = remove_html_tags
        self.normalize_punctuation = normalize_punctuation  

        self._check_errors_()
        self._prepare_lemmatize_()

    def _check_errors_(self):
        if self.lemmatize and self.stem:
            raise ValueError("Lemmatize and Stem are exclusive. Choose one.")

        if self.remove_emojis and self.convert_emojis:
            raise ValueError(
                "Remove emojis and convert emojis are exclusive. Choose one."
            )
        if self.remove_emoticons and self.convert_emoticons:
            raise ValueError(
                "Remove emoticons and convert emoticons are exclusive. Choose one."
            )
        if self.split_hashtags and self.remove_hashtags:
            raise ValueError(
                "Split hashtags and remove hashtags are exclusive. Choose one."
            )
        if self.remove_stopwords and self.stopwords_list is None:
            raise ValueError(
                "If remove stopwords is True, you must provide a type of stopwords list ('default', 'extended', 'nltk', 'spacy') or a list of stopwords."
            )

    def _prepare_stopwords_(self, type_stopwords):
        if type_stopwords == "default":
            from spanish_nlp.utils.stopwords import default_stopwords

            self.stopwords_list = default_stopwords

        elif type_stopwords == "extended":
            from spanish_nlp.utils.stopwords import extended_stopwords

            self.stopwords_list = extended_stopwords

        elif type_stopwords == "nltk":
            import nltk

            nltk.download("stopwords")
            from nltk.corpus import stopwords

            self.stopwords_list = stopwords.words("spanish")
        elif type_stopwords == "spacy":
            import es_core_news_sm

            nlp = es_core_news_sm.load(
                disable=["ner", "parser", "tagger", "textcat", "vectors"]
            )
            self.stopwords_list = nlp.Defaults.stop_words
            del nlp

        elif type_stopwords is None:
            self.stopwords_list = None

        else:
            if type(type_stopwords) == list:
                self.stopwords_list = type_stopwords
            else:
                raise ValueError(
                    "Stopwords must be a list or one of the following: 'default', 'extended', 'nltk', 'spacy'"
                )

    def _prepare_lemmatize_(self):
        if self.lemmatize:
            import es_core_news_sm

            self.nlp_spacy = es_core_news_sm.load(
                disable=["ner", "parser", "tagger", "textcat", "vectors"]
            )

    def _debug_method_(self, text, method_name):
        print(f"Method: {method_name}")
        print("---" * 30)
        print(f"Text: {text}")
        print("===" * 40)

    def _lower_(self, text):
        return text.lower()

    def _remove_url_(self, text):
        url_pattern = re.compile(r"https?://\S+|www\.\S+")
        return url_pattern.sub(r"", text)

    def _remove_hashtags_(self, text):
        """Remove hashtags from text"""
        return text.replace(" #", " ").replace("#", " ")

    def _split_hashtags_(self, text):
        """Split hashtags from text.
        Example:
            * #HolaMundo -> Hola Mundo
        """
        # Find all hashtags
        hashtags = re.findall(r"#(\w+)", text)
        # Split all hashtags and replace them in the text
        pattern = re.compile(
            r"[A-ZÑÁÉIÓÚ][a-zñáéíóúü0-9]+|\d+|[A-ZÑÁÉIÓÚ]+(?![a-zñáéíóúü])"
        )
        for ht in hashtags:
            words = " ".join(pattern.findall(ht)).strip()
            text = text.replace(f"#{ht}", f"{words}")
        return text

    def _normalize_breaklines_(self, text):
        """Convert multiple breaklines to one breakline"""
        text = text.replace("\r", "\n")
        text = re.sub(r"(\n){2,}", r"\n", text)
        return text

    def _emoticons_to_text_(self, text):
        return demoticonize(text, delimiters=(" __", "__ "))

    def _emojis_to_text_(self, text):
        return emoji.demojize(text, delimiters=(" __", "__ "))

    def _text_to_emojis_(self, text):
        return emoji.emojize(text, delimiters=("__", "__"))

    def _text_to_emoticons_(self, text):
        return emoticonize(text, delimiters=("__", "__"))

    def _normalize_inclusive_language_(self, text, inclusive_character="x"):
        """TODO: implement inclusive language normalization"""
        return text

    def _reduce_spam_(self, text):
        """Reduce spam in text when a expression is repeated more than 3 times.
        Example: "hola hola hola hola hola hola" -> "hola hola hola" """
        text = re.sub(r"(\w+\s)\1+", r"\1\1", text)
        text = re.sub(r"(\b(\w+\s){3})\1+", r"\1\1", text)
        return text

    def _remove_vowels_accents_(self, text):
        """Convert vowels with accents from text (lowercase or uppercase)"""
        text = re.sub(r"[áàäâ]", "a", text)
        text = re.sub(r"[éèëê]", "e", text)
        text = re.sub(r"[íìïî]", "i", text)
        text = re.sub(r"[óòöô]", "o", text)
        text = re.sub(r"[úùüû]", "u", text)
        text = re.sub(r"[ÁÀÄÂ]", "A", text)
        text = re.sub(r"[ÉÈËÊ]", "E", text)
        text = re.sub(r"[ÍÌÏÎ]", "I", text)
        text = re.sub(r"[ÓÒÖÔ]", "O", text)
        text = re.sub(r"[ÚÙÜÛ]", "U", text)
        return text

    def _remove_punctuation_(self, text):
        pattern = re.compile(r"[^\w\sáéíóúüñÁÉÍÓÚÜÑ]")
        t = pattern.sub(r" ", text)
        return re.sub(" +", " ", t)

    def _remove_unprintable_(self, text):
        printable = set(string.printable + "ñáéíóúü" + "ÑÁÉÍÓÚÜ")
        text = "".join(filter(lambda x: x in printable, text))
        return text

    def _remove_numbers_(self, text):
        """Remove numbers from text"""
        return re.sub(r"\d+", "", text)

    def _convert_numbers_(self, text, delimiters=(" __", "__ ")):
        return re.sub(r"[0-9]", delimiters[0] + "numero" + delimiters[1], text)

    def _remove_stopwords_(self, text):
        return " ".join(
            [word for word in str(text).split() if word not in self.stopwords_list]
        )

    def _stem_(self, text, stemmer=SnowballStemmer("spanish")):
        """TODO: add another stemmers"""
        return " ".join([stemmer.stem(word) for word in text.split()])

    def _lemmatize_(self, text, lemmatizer="es_core_news_sm"):
        """Lemmatize text using es_core_news_sm from spacy by default"""
        doc = self.nlp_spacy(text)
        return " ".join([token.lemma_ for token in doc])

    def _remove_multiples_spaces_(self, text):
        return re.sub(" +", " ", text)

    def _normalize_punctuation(self, text):
        """Remove all wrong spaces with punctuation"""
        # Remove spaces before punctuation
        text = re.sub(r' +([\.\,\!\?\)\]\}\>\:\#}])', r"\1", text)
        # Remove spaces after punctuation
        text = re.sub(r"([\¡\¿\(\[\{\<])\: +", r"\1", text)
        return text

    def _remove_html_tags_(self, text):
        """Remove html tags from a string"""
        import re

        clean = re.compile("<.*?>")
        return re.sub(clean, "", text)

    def transform(self, text, debug=False):
        if self.split_hashtags:
            text = self._split_hashtags_(text)
            self._debug_method_(text, "split_hashtags") if debug else None

        if self.lower:
            text = self._lower_(text)
            self._debug_method_(text, "lower") if debug else None

        if self.remove_url:
            text = self._remove_url_(text)
            self._debug_method_(text, "remove_url") if debug else None

        if self.remove_html_tags:
            text = self._remove_html_tags_(text)
            self._debug_method_(text, "remove_html_tags") if debug else None

        if self.remove_numbers:
            text = self._remove_numbers_(text)
            self._debug_method_(text, "remove_numbers") if debug else None

        if self.remove_hashtags:
            text = self._remove_hashtags_(text)
            self._debug_method_(text, "remove_hashtags") if debug else None

        if self.stem:
            text = self._stem_(text)
            self._debug_method_(text, "stem") if debug else None

        if self.lemmatize:
            text = self._lemmatize_(text)
            self._debug_method_(text, "lemmatize") if debug else None

        if self.convert_emojis or not self.remove_emojis:
            text = self._emojis_to_text_(text)
            self._debug_method_(text, "emojis_to_text") if debug else None

        if self.convert_emoticons or not self.remove_emoticons:
            text = self._emoticons_to_text_(text)
            self._debug_method_(text, "emoticons_to_text") if debug else None

        if self.normalize_inclusive_language:
            text = self._normalize_inclusive_language_(text)
            self._debug_method_(text, "normalize_inclusive_language") if debug else None

        if self.remove_vowels_accents:
            text = self._remove_vowels_accents_(text)
            self._debug_method_(text, "remove_vowels_accents") if debug else None

        if self.remove_punctuation:
            text = self._remove_punctuation_(text)
            self._debug_method_(text, "remove_punctuation") if debug else None

        if self.remove_unprintable:
            text = self._remove_unprintable_(text)
            self._debug_method_(text, "remove_unprintable") if debug else None

        if self.stem:
            text = self._stem_(text)
            self._debug_method_(text, "stem") if debug else None

        if not self.remove_emojis:
            text = self._text_to_emojis_(text)
            self._debug_method_(
                text, "text_to_emojis (not delete emojis)"
            ) if debug else None

        if not self.remove_emoticons:
            text = self._text_to_emoticons_(text)
            self._debug_method_(
                text, "text_to_emoticons (not delete emoticons)"
            ) if debug else None

        if self.remove_stopwords:
            text = self._remove_stopwords_(text)
            self._debug_method_(text, "remove_stopwords") if debug else None

        if self.remove_multiple_spaces:
            text = self._remove_multiples_spaces_(text).strip()
            self._debug_method_(text, "remove_multiples_spaces") if debug else None

        if self.normalize_breaklines:
            text = self._normalize_breaklines_(text)
            self._debug_method_(text, "normalize_breaklines") if debug else None

        if self.normalize_punctuation:
            text = self._normalize_punctuation(text)
            self._debug_method_(
                text, "normalize_punctuation"
            ) if debug else None

        if self.reduce_spam:
            text = self._reduce_spam_(text)
            self._debug_method_(text, "reduce_spam") if debug else None

        return text
