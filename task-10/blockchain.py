import hashlib
import time
from crypto import verify_signature

class MerkleTree:
    @staticmethod
    def compute_root(transaction_hashes: list[str]) -> str:
        if not transaction_hashes:
            return ""
        
        current_layer = transaction_hashes
        while len(current_layer) > 1:
            next_layer = []
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                right = current_layer[i+1] if i+1 < len(current_layer) else left
                combined = left + right
                next_layer.append(hashlib.sha256(combined.encode('utf-8')).hexdigest())
            current_layer = next_layer
        return current_layer[0]

class Transaction:
    def __init__(self, sender_pub: str, receiver: str, amount: float, signature: str = ""):
        self.sender_pub = sender_pub
        self.receiver = receiver
        self.amount = amount
        self.signature = signature

    @property
    def payload(self) -> str:
        return f"{self.sender_pub}:{self.receiver}:{self.amount}"

    def to_hash(self) -> str:
        return hashlib.sha256(self.payload.encode('utf-8')).hexdigest()

    def is_valid(self) -> bool:
        if self.sender_pub == "SYSTEM": # Mining reward
            return True
        return verify_signature(self.sender_pub, self.signature, self.payload)

class Block:
    def __init__(self, index: int, transactions: list[Transaction], prev_hash: str, difficulty: int):
        self.index = index
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.timestamp = time.time()
        self.nonce = 0
        self.difficulty = difficulty
        self.merkle_root = MerkleTree.compute_root([tx.to_hash() for tx in transactions])
        self.hash = ""

    def compute_hash(self) -> str:
        block_content = f"{self.index}{self.prev_hash}{self.merkle_root}{self.timestamp}{self.nonce}"
        return hashlib.sha256(block_content.encode('utf-8')).hexdigest()

class Blockchain:
    def __init__(self, difficulty: int = 4):
        self.chain: list[Block] = []
        self.difficulty = difficulty
        
        # Create Genesis Block
        genesis = Block(0, [], "0" * 64, self.difficulty)
        genesis.hash = genesis.compute_hash()
        self.chain.append(genesis)

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, block: Block) -> bool:
        if block.index != self.get_last_block().index + 1:
            return False
        if block.prev_hash != self.get_last_block().hash:
            return False
        if not block.hash.startswith("0" * self.difficulty):
            return False
            
        for tx in block.transactions:
            if not tx.is_valid():
                return False

        self.chain.append(block)
        return True

    def calculate_balances(self) -> dict[str, float]:
        balances = {}
        for block in self.chain:
            for tx in block.transactions:
                # Add to receiver
                balances[tx.receiver] = balances.get(tx.receiver, 0.0) + tx.amount
                
                # Subtract from sender
                if tx.sender_pub != "SYSTEM":
                    # For simplicity in this display task, we assume sender address format matches receiver
                    # In a real system, we'd derive the address from the pubkey here.
                    from_addr = f"0x{tx.sender_pub[:4]}...{tx.sender_pub[-4:]}"
                    balances[from_addr] = balances.get(from_addr, 0.0) - tx.amount
        return balances
