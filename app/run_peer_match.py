import argparse
from app.models.peer_matcher import find_closest_peers, apply_peer_multiples
from app.utils.loader import load_company_data, create_company_vector
from app.utils.helpers import validate_vector
from app.models.dcf_generator import run_dcf_from_inputs  # ✅ use helper
from utils.valuation import combine_valuations

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--company_name", required=False, help="Name of the company to evaluate")
    args = parser.parse_args()

    if args.company_name:
        print(f"✅ load_company_data called with: {args.company_name}")
        target_vector, peer_data = load_company_data(args.company_name)
        print(f"📄 Types in peer_data: {[type(p) for p in peer_data]}")

        # Validate and regenerate peer vectors if needed
        for peer in peer_data:
            if isinstance(peer, dict):
                if "vector" not in peer or not validate_vector(peer["vector"]):
                    peer_name = peer.get("name", "UNKNOWN")
                    print(f"⚠️ Recreating vector for peer: {peer_name}")
                    peer["vector"] = create_company_vector(peer)

        print(f"🔍 Matching against: {args.company_name.strip().lower()}")
        for peer in peer_data:
            print(f"👀 {peer.get('name')} ➔ {peer.get('name', '').strip().lower() == args.company_name.strip().lower()}")

        # Get the target peer
        target_peer = next(
            (
                peer for peer in peer_data
                if isinstance(peer, dict) and peer.get("name", "").strip().lower() == args.company_name.strip().lower()
            ),
            None
        )
    else:
        print("📊 No company_name provided, using sample peer for demo.")
        top_peers = [
            {'name': 'Sample Peer A', 'description': "Enterprise software and cloud infrastructure provider"},
            {'name': 'Sample Peer B', 'vector': create_company_vector({'description': "Enterprise AI SaaS platform"})},
            {'name': 'Sample Peer C', 'vector': create_company_vector({'description': "Digital payment gateway and fintech"})}
        ]
        print("\n📈 Top Peers and Estimated Valuations:")
        print(f"# Type of top_peers[0]: {type(top_peers[0])}, Length: {len(top_peers[0])}")
        for peer, similarity in top_peers:
            print(f"✅ {peer['name']} | Similarity: {similarity:.2f}")
        return

    # Run similarity matching
    top_peers = find_closest_peers(target_vector, peer_data)

    print("\n📈 Top Peers and Estimated Valuations:")
    print(f"Type of top_peers[0]: {type(top_peers[0])}, Length: {len(top_peers[0])}")
    for peer, similarity in top_peers:
        print(f"✅ {peer['name']} | Similarity: {similarity:.2f}")

    # Apply peer multiples
    peer_based_valuation = apply_peer_multiples(
        target_peer,
        [p for p, _ in top_peers],
        multiple_type="ev_ebitda"
    )
    print(f"\n📊 Peer-Based Valuation (EV/EBITDA): {peer_based_valuation}")

    # Handle missing DCF value using run_dcf_from_inputs()
    dcf_raw = target_peer.get("dcf_value")
    if not dcf_raw:
        print("⚠️ DCF value missing — generating forecast and valuation...")
        try:
            dcf_value = run_dcf_from_inputs(target_peer)
            target_peer["dcf_value"] = dcf_value
        except Exception as e:
            print(f"❌ Failed to generate DCF: {e}")
            dcf_value = 0.0
    else:
        dcf_value = float(dcf_raw[0]) if isinstance(dcf_raw, list) else float(dcf_raw)

    print(f"⚠️ Types — dcf_value: {type(dcf_value)}, peer_value: {type(peer_based_valuation)}")

    # Combine valuation methods
    valuation_summary = combine_valuations(
        dcf_value=dcf_value,
        peer_value=peer_based_valuation,
        dcf_weight=0.5
    )

    print(f"\n✅ Final Combined Valuation Summary: {valuation_summary}")

if __name__ == "__main__":
    main()
