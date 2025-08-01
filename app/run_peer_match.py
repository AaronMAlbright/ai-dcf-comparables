import argparse
from app.models.peer_matcher import find_closest_peers
from app.utils.loader import load_company_data, create_company_vector
from app.utils.helpers import validate_vector


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--company_name", required=False, help="Name of the company to evaluate")
    args = parser.parse_args()

    if args.company_name:
        print(f"✅ load_company_data called with: {args.company_name}")
        peer_data = load_company_data()

        # Validate and regenerate peer vectors if needed
        for peer in peer_data:
            if not validate_vector(peer.get("vector", None)):
                print(f"⚠️ Recreating vector for peer: {peer.get('name', 'UNKNOWN')}")
                peer["vector"] = create_company_vector(peer)

        # Identify target company
        target_company = next((c for c in peer_data if c["name"] == args.company_name), None)
        if not target_company:
            raise ValueError(f"❌ Target company '{args.company_name}' not found in peer data.")

        target_vector = target_company.get("vector")
        if not validate_vector(target_vector):
            print(f"⚠️ Recreating vector for target company: {args.company_name}")
            target_vector = create_company_vector(target_company)

        # Run peer matching
        top_peers = find_closest_peers(target_vector, peer_data, top_k=3)

    else:
        # Fallback for no CLI input
        print("⚠️ No company_name provided, using sample peer for demo.")
        top_peers = [{
            'name': "Sample Peer A",
            'description': "Enterprise software and cloud infrastructure provider",
            'revenue_base': 2000,
            'revenue_growth': 0.12,
            'ebitda_margin': 0.35,
            'depreciation_pct': 0.06,
            'interest_expense': 50,
            'debt': 1000,
            'capex_pct': 0.05,
            'nwc_pct': 0.04,
            'tax_rate': 0.21,
            'terminal_growth': 0.025
        }]

    print("\n📊 Top Peers and Estimated Valuations:")
    for peer, score in top_peers:
        print(f"✅ {peer['name']} | Similarity: {score:.2f}")


if __name__ == "__main__":
    main()
