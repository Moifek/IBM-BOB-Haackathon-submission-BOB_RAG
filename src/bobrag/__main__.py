"""CLI entry point for BobRAG-MD."""

import sys
import argparse
import logging
from pathlib import Path

from .pipeline import BobRAGPipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_ingest(args):
    """Ingest documents into Qdrant."""
    pipeline = BobRAGPipeline()
    pipeline.ingest(corpus_dir=args.corpus_dir)
    print(f"✓ Ingestion complete from {args.corpus_dir}")


def cmd_query(args):
    """Query the RAG system."""
    pipeline = BobRAGPipeline()
    result = pipeline.query(args.question)
    
    print("\n" + "="*60)
    print(f"Question: {result['question']}")
    print("="*60)
    print(f"\nAnswer:\n{result['answer']}")
    print("\n" + "-"*60)
    print(f"Retrieved {len(result['contexts'])} contexts:")
    for i, ctx in enumerate(result['contexts'], 1):
        print(f"  {i}. {ctx['source']} (score: {ctx['score']:.3f})")
    print("="*60 + "\n")


def cmd_serve(args):
    """Start MCP server."""
    print("Starting MCP server...")
    print("Note: MCP server implementation in src/codebase_mcp/")
    print("Run: uv run python -m src.codebase_mcp.server")
    sys.exit(1)


def cmd_eval(args):
    """Run Ragas evaluation."""
    print("Running Ragas evaluation...")
    print("Note: Evaluation implementation in eval/")
    print("This is a placeholder for the hackathon demo.")
    sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="bobrag",
        description="BobRAG-MD: Minimal medical RAG for IBM Bob Hackathon"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents")
    ingest_parser.add_argument(
        "--corpus-dir",
        default="data/corpus",
        help="Directory containing documents to ingest"
    )
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query the RAG system")
    query_parser.add_argument("question", help="Question to ask")
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start MCP server")
    
    # Eval command
    eval_parser = subparsers.add_parser("eval", help="Run Ragas evaluation")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "ingest":
            cmd_ingest(args)
        elif args.command == "query":
            cmd_query(args)
        elif args.command == "serve":
            cmd_serve(args)
        elif args.command == "eval":
            cmd_eval(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
