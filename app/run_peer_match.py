import argparse
import json
import os
from colorama import Fore, Style

from app.services.peer_matcher_service import run_peer_match_pipeline


def main():
    print(f"{Fore.CYAN}🚀 RUN_PEER_MATCH.PY STARTED{Style.RESET_ALL}")

    parser = argparse.ArgumentParser()
    parser.add_argument("--company_name", required=False, help="Name of the company to evaluate")
    parser.add_argument("--wacc", type=float, default=0.10, help="Discount rate for DCF")
    parser.add_argument("--terminal_growth", type=float, default=0.03, help="Terminal growth rate for DCF")
    parser.add_argument("--dcf_weight", type=float, default=0.5, help="Weight to assign to DCF in final valuation")
    parser.add_argument("--top_n_peers", type=int, default=5, help="Number of top peers to consider")
    parser.add_argument("--min_similarity", type=float, default=0.0, help="Minimum similarity threshold for peers")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--output_json", action="store_true", help="Output final results to JSON")
    parser.add_argument(
        "--multiple_type",
        choices=["ev_ebitda", "pe_ratio"],
        default="ev_ebitda",
        help="Type of peer multiple to use for valuation"
    )
    parser.add_argument(
        "--export_peers",
        action="store_true",
        help="Export full peer similarity table to CSV"
    )

    args = parser.parse_args()

    result = run_peer_match_pipeline(
        company_name=args.company_name,
        wacc=args.wacc,
        terminal_growth=args.terminal_growth,
        dcf_weight=args.dcf_weight,
        top_n_peers=args.top_n_peers,
        min_similarity=args.min_similarity,
        verbose=args.verbose,
        output_json=args.output_json,
        multiple_type=args.multiple_type,
        export_peers=args.export_peers,
    )

    if result is None:
        print(f"{Fore.RED}❌ Peer match pipeline failed or returned no results.{Style.RESET_ALL}")
        return

    print(f"\n{Fore.YELLOW}📊 FINAL OUTPUT SUMMARY:{Style.RESET_ALL}")
    print(json.dumps(result, indent=2))

    if args.output_json:
        os.makedirs("results", exist_ok=True)
        output_path = "results/output_summary.json"
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"{Fore.GREEN}📝 Results saved to {output_path}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
