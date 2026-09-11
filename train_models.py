"""Model-training entry point.

Phase 2 deliberately disables model training so the old synthetic artifacts cannot
be regenerated. Prepare validated source data first; Phase 3 will introduce the
real content-based training command.
"""


def main() -> int:
    print("Model training is not available during Phase 2.")
    print("Prepare validated source data instead:")
    print("  python prepare_data.py")
    print("Phase 3 will add real content-based model training.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
