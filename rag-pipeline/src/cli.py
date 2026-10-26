import argparse
from src.chain import build_chain


def main():
    parser = argparse.ArgumentParser(
        description="Ask a question against your local documents."
    )
    parser.add_argument("question", help="Question to ask")
    parser.add_argument(
        "--show-chunks",
        action="store_true",
        help="Print the retrieved chunks used to answer",
    )
    args = parser.parse_args()

    ask = build_chain()
    result = ask(args.question)

    print("\n=== ANSWER ===")
    print(result["answer"])

    print("\n=== SOURCES ===")
    for src in sorted(set(result["sources"])):
        print(f"- {src}")

    if args.show_chunks:
        print("\n=== RETRIEVED CHUNKS ===")
        for i, chunk in enumerate(result["chunks"], 1):
            print(f"\n[Chunk {i}]")
            print(chunk)


if __name__ == "__main__":
    main()