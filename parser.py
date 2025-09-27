import glob
import os
import sys
import struct
from collections import Counter
from typing import List, Dict, Optional


def max_counter(a_: List[int], b_: List[int]) -> Counter:
    a = Counter(a_)
    b = Counter(b_)
    c = Counter()
    for k in set(a.keys()).union(set(b.keys())):
        c[k] = max(a[k], b[k])
    l = []
    for k, v in c.items():
        l.extend([k] * v)
    return l


class YDCDeck:
    def __init__(self, main: List[int] = [], side: List[int] = [], fusion: List[int] = []):
        self.main = main
        self.side = side
        self.fusion = fusion

    def extend(self, other) -> None:
        self.main = max_counter(self.main, other.main)
        self.side = max_counter(self.side, other.side)
        self.fusion = max_counter(self.fusion, other.fusion)

    def __repr__(self):
        return (f"<YDCDeck main={len(self.main)} "
                f"fusion={len(self.fusion)} "
                f"side={len(self.side)}>")


def parse_card_list(path: str) -> Dict[int, str]:
    """
    Parse card_list.txt to map card IDs -> names.
    """
    id_to_name: Dict[int, str] = {}
    current_name: Optional[str] = None

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line.startswith("//") and not "[" in line:
                # Line with name
                name = line.lstrip("/").strip()
                if name:
                    current_name = name
            elif "[" in line and "]" in line:
                # Line with ID
                try:
                    inside = line.split("[")[1].split("]")[0]
                    card_id = int(inside)
                    if current_name:
                        id_to_name[card_id] = current_name
                        current_name = None
                except ValueError:
                    continue
    return id_to_name


def parse_ydc(data: bytes, debug: bool = False) -> YDCDeck:
    # --- Header ---
    header = data[:8]
    version, hdrlen, magic = struct.unpack("<HHI", header)
    if debug:
        print(
            f"Header: version={version}, hdrlen={hdrlen}, magic=0x{magic:08X}")
    offset = 8

    # --- Main Deck ---
    main_count = struct.unpack_from("<H", data, offset)[0]
    offset += 2
    main_cards = list(struct.unpack_from(
        f"<{main_count}H", data, offset)) if main_count else []
    offset += main_count * 2
    if debug:
        print(f"Main deck ({main_count}): {main_cards}")

    # --- Fusion Deck ---
    fusion_count = struct.unpack_from("<H", data, offset)[0]
    offset += 2
    fusion_cards = list(struct.unpack_from(
        f"<{fusion_count}H", data, offset)) if fusion_count else []
    offset += fusion_count * 2
    if debug:
        print(f"Fusion deck ({fusion_count}): {fusion_cards}")

    # --- Side Deck ---
    side_count = struct.unpack_from("<H", data, offset)[0]
    offset += 2
    side_cards = list(struct.unpack_from(
        f"<{side_count}H", data, offset)) if side_count else []
    offset += side_count * 2
    if debug:
        print(f"Side deck ({side_count}): {side_cards}")

    return YDCDeck(main_cards, side_cards, fusion_cards)


def pretty_print(deck: YDCDeck, id_to_name: Optional[Dict[int, str]] = None, print=print):
    def lookup(ids: List[int]) -> List[str]:
        if not id_to_name:
            return [f"0x{id:04X}" for id in ids]
        return [id_to_name.get(id, f'0x{id:04X}') for id in ids]

    def count(names: List[str]) -> List[str]:
        return [f"{cnt}x {name}" for name, cnt in Counter(names).items()]

    print("// Main deck\n" + '\n'.join(count(lookup(deck.main))))
    print("// Fusion deck\n" + '\n'.join(count(lookup(deck.fusion))))
    print("// Side deck\n" + '\n'.join(count(lookup(deck.side))))


def process(filename: str, cardlist_path: str,
            debug: bool, print=print) -> YDCDeck:
    with open(filename, "rb") as f:
        data = f.read()
    deck = parse_ydc(data, debug=debug)

    # Load card list if provided
    id_to_name = None
    if cardlist_path:
        id_to_name = parse_card_list(cardlist_path)

    print(f'// {os.path.basename(filename)} {deck}')
    # Pretty print result
    pretty_print(deck, id_to_name, print=print)
    return deck


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <deck.ydc> [card_list.txt] [--debug]")
        sys.exit(1)

    filename = sys.argv[1]
    cardlist_path = None
    debug = False

    for arg in sys.argv[2:]:
        if arg == "--debug":
            debug = True
        else:
            cardlist_path = arg

    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' does not exist.")
        exit(1)

    # Parse and print deck
    process(filename, cardlist_path, debug)


if __name__ == "__main__":
    main()
