import spacy
nlp = spacy.load("en_core_web_md")

def similarity(a,b):
    return a.similarity(b)

sentence = "I love you and I want to sleep with you"
doc = nlp(sentence)

while similarity <= .8:
    user_sentence = input("Guess my sentence")
    doc2 = nlp(user_sentence)
    for i in doc2:
        similarity