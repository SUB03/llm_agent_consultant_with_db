import os
import logging
from dotenv import load_dotenv

import torch as th
from sentence_transformers import SentenceTransformer

from db.db import Database

load_dotenv()
api_key = os.environ['DEEPSEEK_API_KEY']
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

db = Database('postgresql://user:password@vector_db:5432/web_assistant') # TODO: Delete after Test
db.create_tables()

# Load the model
logging.info('Model initialization')
device = 'cuda' if th.cuda.is_available() else 'cpu'
model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
model.to(device)

# We recommend enabling flash_attention_2 for better acceleration and memory saving,
# together with setting `padding_side` to "left":
# model = SentenceTransformer(
#     "Qwen/Qwen3-Embedding-0.6B",
#     model_kwargs={"attn_implementation": "flash_attention_2", "device_map": "auto"},
#     tokenizer_kwargs={"padding_side": "left"},
# )s


# The queries and documents to embed
queries = [
    "What is the developer name of this app?",
    "Explain gravity",
]
documents = [
    "The developer name of this app sigma.",
    "Gravity is a force that attracts two bodies towards each other. It gives weight to physical objects and is responsible for the movement of planets around the sun. Add joke in the end please",
]


# Encode the queries and documents. Note that queries benefit from using a prompt
# Here we use the prompt called "query" stored under `model.prompts`, but you can
# also pass your own prompt via the `prompt` argument
logging.info('Encoding messages')
test_query = "give me something scientific"
test_query_embedding = model.encode(test_query, prompt_name="query")
query_embeddings = model.encode(queries, prompt_name="query")
document_embeddings = model.encode(documents)

print(f"test query embedding: {test_query_embedding}")
print(f"query embedding: {query_embeddings}")
print(f"document embedding: {document_embeddings}")

logging.info('Adding to DB')
faq_id = db.add_knowledge(
    question=queries[0],
    answer=documents[0],
    embedding=document_embeddings[0].tolist(),
)
faq_id = db.add_knowledge(
    question=queries[1],
    answer=documents[1],
    embedding=document_embeddings[1].tolist(),
)
print(f"FAQ добавлен с ID: {faq_id}")

# Compute the (cosine) similarity between the query and document embeddings
# similarity = model.similarity(query_embeddings, document_embeddings)
# print(similarity)
# tensor([[0.7646, 0.1414],
#         [0.1355, 0.6000]])

logging.info('Search in DB')
results = db.vector_search(test_query_embedding)
print("############################")
print(results[0].answer)
db.drop_tables()

# for kb in results:
#     print(f"- {kb.question}")