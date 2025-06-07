from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

# Load tokenizer and model
model_name = "dslim/bert-base-NER"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

# Create NER pipeline
nlp_ner = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# Try it on some text
text = "I would very much like to take an airplane to the great city of Chicago and see my good great friends Josh and Adam."

entities = nlp_ner(text)

for entity in entities:
    print(f"{entity['word']} → {entity['entity_group']} ({entity['score']:.2f})")
