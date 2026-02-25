import heapq


class Node:
    def __init__(self, n, val='internal'):
        self.n = n
        self.val = val
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.n < other.n


huffman = {}


def preOrder(node, curr):
    if not node:
        return

    if not node.left and not node.right:
        huffman[node.val] = curr
        return

    preOrder(node.left, curr + '0')
    preOrder(node.right, curr + '1')


freq = {
    'a': 5,
    'b': 9,
    'c': 12,
    'd': 13,
    'e': 16,
    'f': 45
}

heap = [Node(v, k) for k, v in freq.items()]
heapq.heapify(heap)

while len(heap) > 1:
    left = heapq.heappop(heap)

    right = heapq.heappop(heap)

    newNode = Node(left.n + right.n)
    newNode.left, newNode.right = left, right
    heapq.heappush(heap, newNode)

root = heapq.heappop(heap)

preOrder(root, "")

print(huffman)
