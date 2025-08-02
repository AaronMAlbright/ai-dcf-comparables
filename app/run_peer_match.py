import argparse
import json
import os

from app.models.peer_matcher import find_closest_peers, prepare_vectors
from app.utils.helpers import validate_vector
from app.models.dcf_generator import run_dcf_from_inputs
from app.utils.valuation import combine_valuations, estimate_peer_valuation
from app.utils.loader import create_company_vector

def main():
    print("\U0001F680 RUN_PEER_MATCH.PY STARTED")

    parser = argparse.ArgumentParser()
    parser.add_argument("--company_name", required=False, help="Name of the company to evaluate")
    parser.add_argument("--wacc", type=float, default=0.10, help="Discount rate for DCF")
    parser.add_argument("--terminal_growth", type=float, default=0.03, help="Terminal growth rate for DCF")
    parser.add_argument("--dcf_weight", type=float, default=0.5, help="Weight to assign to DCF in final valuation")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--output_json", action="store_true", help="Output final results to JSON")
    parser.add_argument("--top_n_peers", type=int, default=5, help="Max number of similar peers to return")
    parser.add_argument("--min_similarity", type=float, default=0.0, help="Minimum similarity score required for a peer to be included")
    args = parser.parse_args()

    if args.company_name:
        print(f"✅ Running analysis for: {args.company_name}")

        target_vector, peer_data = prepare_vectors(args.company_name)
        print("DEBUG peer_data types after prepare_vectors:", [type(p) for p in peer_data])

        print(f"🔍 Debugging peer_data contents:")
        for i, p in enumerate(peer_data):
            print(f"  Index {i}: Type: {type(p)}, Preview: {str(p)[:80]}")

        valid_peers = [p for p in peer_data if isinstance(p, dict)]
        removed_peers = [p for p in peer_data if not isinstance(p, dict)]

        if removed_peers:
            print(f"⚠️ Removed {len(removed_peers)} malformed peer entries (not dicts): {removed_peers}")

        peer_data = valid_peers

        if args.verbose:
            print("\n🧪 Validating peer inputs:")
            for peer in peer_data:
                print(f"→ {peer.get('name')}, Desc: {peer.get('description', '')[:40]}..., "
                      f"RG: {peer.get('revenue_growth')}, EBITDA: {peer.get('ebitda_margin')}, "
                      f"CAPEX: {peer.get('capex_pct')}, "
                      f"Vector Valid: {validate_vector(peer.get('vector'))}, "
                      f"Vector Sample: {str(peer.get('vector'))[:50]}")

        target_peer = next(
            (
                peer for peer in peer_data
                if peer.get("name", "").strip().lower() == args.company_name.strip().lower()
            ),
            None
        )

        if not target_peer:
            print(f"❌ Could not find target company: {args.company_name}")
            return

        print(f"🎯 Target vector sample: {target_vector[:5]}")
        print(f"👥 Sample peer vector: {peer_data[0].get('vector', [])[:5] if peer_data else 'N/A'}")
    else:
        print("📊 No company_name provided, using sample demo peers.")
        top_peers = [
            {'name': 'Sample Peer A', 'description': "Enterprise software and cloud infrastructure provider"},
            {'name': 'Sample Peer B', 'vector': create_company_vector({'description': "Enterprise AI SaaS platform"})},
            {'name': 'Sample Peer C', 'vector': create_company_vector({'description': "Digital payment gateway and fintech"})}
        ]
        print("\n📈 Top Peers and Estimated Valuations:")
        for peer in top_peers:
            print(f"✅ {peer['name']}")
        return

    top_peers = find_closest_peers(
        target_vector,
        peer_data,
        top_k=args.top_n_peers,
        target_name=args.company_name
    )

    if args.min_similarity > 0:
        original_count = len(top_peers)
        top_peers = [(p, s) for (p, s) in top_peers if s >= args.min_similarity]
        filtered_count = len(top_peers)
        print(f"⚠️ Filtered peers below min_similarity={args.min_similarity} → {original_count} → {filtered_count}")

    print(f"🧪 Returned {len(top_peers)} peers from find_closest_peers()")
    if top_peers:
        print(f"📊 Top match: {top_peers[0][0].get('name', 'Unknown')} | Score: {top_peers[0][1]:.4f}")
    else:
        print("❗ No peers matched — check similarity logic or vector inputs.")

    print("\n📈 Top Peers and Estimated Valuations:")
    for peer, similarity in top_peers:
        print(f"✅ {peer['name']} | Similarity: {similarity:.2f}")

    print(f"📎 Sending {len(top_peers)} peers into estimate_peer_valuation()")
    peer_result = estimate_peer_valuation([p for p, _ in top_peers], target_peer)
    print(f"\n📊 Peer-Based Valuation (EV/EBITDA): {peer_result}")

    dcf_raw = target_peer.get("dcf_value")
    if not dcf_raw:
        print("⚠️ DCF value missing — generating forecast and valuation...")
        try:
            dcf_value = run_dcf_from_inputs(
                target_peer,
                wacc=args.wacc,
                terminal_growth=args.terminal_growth
            )
            target_peer["dcf_value"] = dcf_value
        except Exception as e:
            print(f"❌ Failed to generate DCF: {e}")
            dcf_value = 0.0
    else:
        dcf_value = float(dcf_raw[0]) if isinstance(dcf_raw, list) else float(dcf_raw)

    valuation_summary = combine_valuations(
        dcf_value=dcf_value,
        peer_value=peer_result,
        dcf_weight=args.dcf_weight
    )

    if valuation_summary is not None:
        print(f"\n✅ Final Combined Valuation Summary: {valuation_summary:.2f}")

        result_data = {
            "company_name": args.company_name,
            "dcf_value": dcf_value,
            "peer_value": peer_result.get("implied_value") if isinstance(peer_result, dict) else peer_result,
            "combined_valuation": valuation_summary,
            "top_peers": [
                {
                    "peer_name": peer.get("name"),
                    "similarity": round(score, 4),
                    "ev_ebitda": peer.get("ev_ebitda"),
                }
                for peer, score in top_peers
            ]
        }

        if args.output_json:
            os.makedirs("results", exist_ok=True)
            output_path = f"results/output_summary.json"
            with open(output_path, "w") as f:
                json.dump(result_data, f, indent=2)
            print(f"📝 Results saved to {output_path}")
    else:
        print("\n❌ Final Combined Valuation Summary: Could not be computed due to invalid inputs.")

if __name__ == "__main__":
    main()
