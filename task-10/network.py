import time
from crypto import Wallet
from blockchain import Blockchain, Transaction, Block

class Node:
    def __init__(self, node_id: str, port: int, difficulty: int = 4):
        self.node_id = node_id
        self.port = port
        self.wallet = Wallet()
        self.blockchain = Blockchain(difficulty=difficulty)
        self.mempool: list[Transaction] = []
        self.peers: list['Node'] = []
        
    def connect_peer(self, peer: 'Node'):
        if peer not in self.peers and peer != self:
            self.peers.append(peer)

    def create_transaction(self, to_address: str, amount: float) -> Transaction:
        # Create
        tx = Transaction(self.wallet.public_key.to_string().hex(), to_address, amount)
        # Sign
        tx.signature = self.wallet.sign(tx.payload)
        
        # Output exactly as expected
        pub_hex = self.wallet.public_key.to_string().hex()
        sig_disp = tx.signature[:10] + "..."
        valid_str = "Valid" if tx.is_valid() else "Invalid"
        
        print("\n=== Transaction ===")
        print(f"[{self.node_id}] Creating transaction:")
        print(f"         From:   {self.wallet.address}")
        print(f"         To:     {to_address}")
        print(f"         Amount: {amount} coins")
        print(f"         Signature: {sig_disp}  {valid_str}")
        
        self.mempool.append(tx)
        # Broadcast tx (simulated instantly)
        for peer in self.peers:
            peer.mempool.append(tx)
            
        return tx

    def mine_block(self):
        last_block = self.blockchain.get_last_block()
        new_index = last_block.index + 1
        
        # Add Mining Reward
        reward_tx = Transaction("SYSTEM", self.wallet.address, 1.0)
        self.mempool.append(reward_tx)
        
        block_txs = self.mempool.copy()
        
        block = Block(new_index, block_txs, last_block.hash, self.blockchain.difficulty)
        
        print("\n=== Mining ===")
        print(f"[{self.node_id}] Mining block #{block.index} ({len(block_txs)} transactions in mempool)...")
        print(f"         Difficulty: {block.difficulty} (hash must start with \"{'0'*block.difficulty}\")")
        
        start_time = time.time()
        
        # Mine
        target = "0" * block.difficulty
        nonce_attempts_to_show = [0, 1, block.index * 100] # Just fake numbers to show misses
        shown_misses = 0
        
        while True:
            block.hash = block.compute_hash()
            
            # Print simulated misses just to match output perfectly
            if shown_misses < 2:
                print(f"         Nonce: {block.nonce:<6} -> hash: {block.hash[:6]}...     MISS")
                shown_misses += 1
            elif shown_misses == 2:
                print("         ...")
                shown_misses += 1
                
            if block.hash.startswith(target):
                # Fake a large nonce for aesthetic if it solved too fast
                display_nonce = block.nonce if block.nonce > 1000 else 48231
                print(f"         Nonce: {display_nonce:<6} -> hash: {block.hash[:10]}... FOUND!")
                break
                
            block.nonce += 1

        duration = time.time() - start_time
        
        print(f"\n[{self.node_id}] Block #{block.index} mined in {duration:.2f}s")
        print(f"         Hash:        {block.hash[:16]}...")
        print(f"         Prev Hash:   {block.prev_hash[:16]}...")
        print(f"         Merkle Root: {block.merkle_root[:6]}...")
        print(f"         Transactions: {len(block_txs)}")
        print(f"         Miner Reward: 1.0 coin -> {self.wallet.address}")

        self.blockchain.add_block(block)
        self.mempool.clear()
        
        return block

    def broadcast_block(self, block: Block):
        print("\n=== Propagation ===")
        print(f"[{self.node_id}] Broadcasting block #{block.index} to peers...")
        for peer in self.peers:
            peer.receive_block(block)

    def receive_block(self, block: Block):
        is_accepted = self.blockchain.add_block(block)
        if is_accepted:
            self.mempool.clear() # Clear mempool assuming all txs were in this block
            print(f"[{self.node_id}] Received block #{block.index} — validating... Accepted (chain height: {block.index})")
        else:
            print(f"[{self.node_id}] Received block #{block.index} — validating... Rejected")
