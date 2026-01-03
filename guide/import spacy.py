import spacy
nlp = spacy.load("en_core_web_md")


sentence = "I love you and I want to sleep with you"
doc = nlp(sentence)
