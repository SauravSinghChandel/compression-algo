import heapq
from collections import Counter


def pack_bits(bitstring: str):
    pad_bits = (-len(bitstring) % 8)
    bitstring_padded = bitstring + ("0" * pad_bits)

    out = bytearray()
    for i in range(0, len(bitstring_padded), 8):
        byte_str = bitstring_padded[i:i+8]
        out.append(int(byte_str, 2))

    return bytes(out), pad_bits


def unpack_bits(data: bytes, pad_bits: int):
    bits = "".join(f"{b:08b}" for b in data)

    if pad_bits:
        bits = bits[:-pad_bits]

    return bits


def huffman_encode(text):

    class Node:
        def __init__(self, n, val='internal'):
            self.n = n
            self.val = val
            self.left = None
            self.right = None

        def __lt__(self, other):
            return self.n < other.n

    if not text:
        return "", {}

    codes = {}
    originalLen = len(text)

    def preOrder(node, curr):
        if not node:
            return

        if not node.left and not node.right:
            codes[node.val] = curr
            return

        preOrder(node.left, curr + '0')
        preOrder(node.right, curr + '1')

    freq = Counter(text)

    heap = [Node(v, k) for k, v in freq.items()]
    heapq.heapify(heap)

    if len(heap) == 1:
        only = heap[0].val
        codes = {only: "0"}
        encoded = "0" * originalLen
        return encoded, codes

    while len(heap) > 1:
        left = heapq.heappop(heap)

        right = heapq.heappop(heap)

        newNode = Node(left.n + right.n)
        newNode.left, newNode.right = left, right
        heapq.heappush(heap, newNode)

    root = heapq.heappop(heap)

    preOrder(root, "")

    encoded = "".join(codes[c] for c in text)
    packed, pad_bits = pack_bits(encoded)

    return packed, codes, originalLen, pad_bits


def huffman_decode(packed, codes, original_len=None, pad_bits=0):
    if not codes:
        return ""

    encoded = unpack_bits(packed, pad_bits)

    rev = {bitstr: sym for sym, bitstr in codes.items()}

    if len(rev) == 1:
        sym = next(iter(rev.values()))
        if original_len is None:
            return sym * len(encoded)
        return sym * original_len

    out = []
    out_len = 0
    buf = ""
    for bit in encoded:
        buf += bit
        if buf in rev:
            out.append(rev[buf])
            out_len += 1
            buf = ""

            if original_len and out_len == original_len:
                break

    if not original_len and buf != "":
        raise ValueError(
            "Invalide encoded bitstream: leftover bits do not form a codeword")

    return "".join(out)


text = "Saurav Singh Chandel"
packed, codes, og, pad_bits = huffman_encode(text)
print(packed)
print("#####################################")
decoded = huffman_decode(packed, codes, og, pad_bits)

print(decoded)
