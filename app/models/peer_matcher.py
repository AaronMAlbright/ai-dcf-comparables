from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def find_closest_peers(target_description, peer_descriptions, top_k=5):
    target_embedding = model.encode(target_description, convert_to_tensor=True)
    peer_embeddings = model.encode(peer_descriptions, convert_to_tensor=True)

    scores = util.cos_sim(target_embedding, peer_embeddings)[0]
    top_results = scores.topk(k=top_k)

    return [(peer_descriptions[i], float(scores[i])) for i in top_results.indices]
