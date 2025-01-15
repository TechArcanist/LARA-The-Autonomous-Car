import pandas as pd
from sentence_transformers import SentenceTransformer

# Load the dataset
faq_dataset = pd.read_csv("Greetings.csv")
# print(faq_dataset.columns)
# Load multilingual embedding model
embedding_model = SentenceTransformer("sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens")

# Create embeddings for the questions
faq_questions = faq_dataset["Question"].tolist()
faq_answers = faq_dataset["Answer"].tolist()

# Generate embeddings for all questions
faq_embeddings = embedding_model.encode(faq_questions, convert_to_tensor=True)

'''
      Multilingual FAQ dataset encode krega jisse hindi english ka verification ho sake 
      But still Hinglish ka kuch krte h '''
