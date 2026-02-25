import heapq
from collections import Counter


def huffmanEncode(text):

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

    return encoded, codes, originalLen


def huffmanDecode(encoded, codes, originalLen=None):
    if not codes:
        return ""

    rev = {bitstr: sym for sym, bitstr in codes.items()}

    if len(rev) == 1:
        sym = next(iter(rev.value()))
        if originalLen is None:
            return sym * len(encoded)
        return sym * originalLen

    out = []
    buf = ""
    for bit in encoded:
        buf += bit
        if buf in rev:
            out.append(rev[buf])
            buf = ""

    if buf != "":
        raise ValueError(
            "Invalide encoded bitstream: leftover bits do not form a codeword")

    return "".join(out)


text = "Saurav singh chandel"
encoded, codes, og = huffmanEncode(text)
print(encoded)
print("#####################################")
decoded = huffmanDecode(encoded, codes, og)

print(decoded)
