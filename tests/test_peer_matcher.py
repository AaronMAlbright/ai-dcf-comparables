import sys
print("Python executable:", sys.executable)


from dcf_app.models.peer_matcher import find_closest_peers

def test_find_closest_peers_output():
    target = "Large technology company focused on cloud computing and enterprise software"
    peers = [
        "Online retailer and web services provider",
        "Search engine and advertising platform",
        "Enterprise software and cloud infrastructure provider"
    ]
    result = find_closest_peers(target, peers, top_k=2)
    assert len(result) == 2
    assert isinstance(result[0], tuple)
