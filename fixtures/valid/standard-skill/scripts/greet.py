"""Greet script fixture — prints Hello, <name>!"""
import argparse

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)
    args = p.parse_args()
    print(f"Hello, {args.name}!")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
