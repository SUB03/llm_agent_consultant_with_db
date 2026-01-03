import os
import logging
from dotenv import load_dotenv

import torch as th
from sentence_transformers import SentenceTransformer

from db.db import Database

load_dotenv()
api_key = os.environ['DEEPSEEK_API_KEY']
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

db = Database('postgresql://user:password@localhost:5434/web_assistant') # TODO: Delete after Test
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
test_query = "do you know developer name?"
test_query_embedding = model.encode(test_query, prompt_name="query")
query_embeddings = model.encode(queries, prompt_name="query")
document_embeddings = model.encode(documents)

print(f"test query embedding: {test_query_embedding}")

logging.info('Adding to DB')
faq_id = db.add_knowledge(
    question=query_embeddings,
    answer=document_embeddings,
    category="Qwen3-Embedding-0.6B",
)
print(f"FAQ добавлен с ID: {faq_id}")

# Compute the (cosine) similarity between the query and document embeddings
# similarity = model.similarity(query_embeddings, document_embeddings)
# print(similarity)
# tensor([[0.7646, 0.1414],
#         [0.1355, 0.6000]])

logging.info('Search in DB')
results = db.search_knowledge(test_query, use_vector=True)
for kb in results:
    print(f"- {kb.question}")