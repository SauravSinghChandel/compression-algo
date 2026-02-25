import heapq
from collections import Counter
import struct

MAGIC = b"SSC0"


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


def serialize_codes(codes: dict[int, str]) -> bytes:
    items = list(codes.items())
    out = bytearray()

    out += struct.pack(">H", len(items))

    for sym, bitstr in items:
        code_len = len(bitstr)
        code_bytes, _ = pack_bits(bitstr)
        nbytes = (code_len + 7) // 8  # ceil(code_len / 8)

        out += struct.pack("B", sym)
        out += struct.pack("B", code_len)
        out += code_bytes[:nbytes]

    return bytes(out)


def deserialize_codes(blob: bytes, offset: int = 0):
    num = struct.unpack_from(">H", blob, offset)[0]
    offset += 2

    codes = {}

    for _ in range(num):
        sym = blob[offset]
        code_len = blob[offset + 1]
        offset += 2

        nbytes = (code_len + 7) // 8
        raw = blob[offset: offset + nbytes]
        offset += nbytes

        bitstr = "".join(f"{b:08b}" for b in raw)[:code_len]
        codes[sym] = bitstr

    return codes, offset


def huffman_encode(data: bytes):

    class Node:
        def __init__(self, n, val='internal', left=None, right=None):
            self.n = n
            self.val = val
            self.left = left
            self.right = right

        def __lt__(self, other):
            return self.n < other.n

    if not data:
        return b"", {}, 0, 0

    codes = {}
    original_len = len(data)

    def preOrder(node, curr):
        if not node:
            return

        if not node.left and not node.right:
            codes[node.val] = curr
            return

        preOrder(node.left, curr + '0')
        preOrder(node.right, curr + '1')

    freq = Counter(data)

    heap = [Node(v, k) for k, v in freq.items()]
    heapq.heapify(heap)

    if len(heap) == 1:
        only = heap[0].val
        codes = {only: "0"}
        encoded_bits = "0" * original_len
        packed, pad_bits = pack_bits(encoded_bits)
        return packed, codes, original_len, pad_bits

    while len(heap) > 1:
        left = heapq.heappop(heap)

        right = heapq.heappop(heap)

        newNode = Node(left.n + right.n, None, left, right)
        heapq.heappush(heap, newNode)

    root = heapq.heappop(heap)

    preOrder(root, "")

    encoded = "".join(codes[b] for b in data)

    packed, pad_bits = pack_bits(encoded)

    return packed, codes, original_len, pad_bits


def huffman_decode(packed, codes, original_len=None, pad_bits=0):
    if not codes:
        return b""

    encoded = unpack_bits(packed, pad_bits)

    # reverse map
    rev = {bitstr: sym for sym, bitstr in codes.items()}

    if len(rev) == 1:
        sym = next(iter(rev.values()))
        return bytes([sym]) * original_len

    out = bytearray()
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

    if out_len != original_len:
        raise ValueError(
            "Decode Failed: did not produce expected number of bytes")

    return bytes(out)


def compress_bytes(data: bytes) -> bytes:
    packed, codes, original_len, pad_bits = huffman_encode(data)

    codes_blob = serialize_codes(codes)

    header = bytearray()
    header += MAGIC
    header += struct.pack(">Q", original_len)
    header += struct.pack("B", pad_bits)
    header += codes_blob

    return bytes(header) + packed


def decompress_bytes(blob: bytes) -> bytes:
    if blob[:4] != MAGIC:
        raise ValueError("Not a valid SSC0 blob")

    original_len = struct.unpack_from(">Q", blob[4:12])[0]
    pad_bits = blob[12]

    offset = 13  # 4 (MAGIC) + 8 (original_len) + 1 (pad_bits)

    codes, offset = deserialize_codes(blob, offset)

    packed = blob[offset:]

    return huffman_decode(packed, codes, original_len, pad_bits)


data = b"Saurav Singh Chandel"
blob = compress_bytes(data)
recovered = decompress_bytes(blob)

assert recovered == data
