from app.models.peer_matcher import find_closest_peers
from app.models.dcf_generator import mock_dcf_valuation

target = "Cloud computing and enterprise software company"
peers = [
    "Online retailer and web services provider",
    "Search engine and advertising platform",
    "Enterprise software and cloud infrastructure provider",
    "Luxury car manufacturer",
    "Retail bank with mortgage services"
]

results = find_closest_peers(target, peers, top_k=3)

print("\nTop Peers and Estimated Valuations:")
for peer, score in results:
    valuation = mock_dcf_valuation(peer)
    print(f"{peer} — Similarity: {round(score, 4)}, DCF: ${round(valuation, 2)}M")

