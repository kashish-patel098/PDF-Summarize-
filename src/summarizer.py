"""Lightweight summarization using sentence extraction.
If transformers are available, user can replace make_summary with a model call.
"""
from typing import Dict
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import heapq
import nltk

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

def extractive_summary(text, max_sentences=5):
    # 1. Tokenize into sentences and words
    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())

    # 2. Filter out stop words
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]

    # 3. Calculate word frequencies
    word_frequencies = {}
    for word in filtered_words:
        if word not in word_frequencies:
            word_frequencies[word] = 0
        word_frequencies[word] += 1

    # 4. Score sentences
    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies:
                if sentence not in sentence_scores:
                    sentence_scores[sentence] = 0
                sentence_scores[sentence] += word_frequencies[word]

    # 5. Select top sentences
    summary_sentences = heapq.nlargest(max_sentences, sentence_scores, key=sentence_scores.get)

    # 6. Construct the summary
    summary = ' '.join(summary_sentences)
    return summary

def make_slide_text(section: Dict) -> Dict:
    """Return: {headline, bullets (list), note}"""
    text = section.get("text", "")
    headline = section.get("title") or extractive_summary(text, max_sentences=1)
    summary = extractive_summary(text, max_sentences=2)
    # derive bullets by splitting summary into short phrases/sentences
    bullets = [s.strip() for s in summary.split('.') if s.strip()][:2]
    note = extractive_summary(text, max_sentences=1)
    return {"headline": headline.strip(), "bullets": bullets, "note": note.strip()}

