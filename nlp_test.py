from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = ["Apple is a tech company", "Microsoft is a cloud provider"]
embeddings = model.encode(sentences, convert_to_tensor=True)

similarity = util.cos_sim(embeddings[0], embeddings[1])
print("Cosine Similarity:", similarity.item())

