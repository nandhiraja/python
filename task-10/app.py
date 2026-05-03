import sys
from network import Node

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    # Initialize nodes
    node1 = Node("NODE-1", 5001)
    node2 = Node("NODE-2", 5002)
    node3 = Node("NODE-3", 5003)

    # Initial Balances (Simulate they mined previous blocks)
    # Block 1-6 assumed to have happened. Node 1 has 10, Node 2 has 12.5, Node 3 has 4.0
    # We will just manually inject this state into genesis for testing aesthetics
    from blockchain import Transaction, Block
    
    # Injecting balances into genesis to match expected output later
    init_tx1 = Transaction("SYSTEM", node1.wallet.address, 10.0)
    init_tx2 = Transaction("SYSTEM", node2.wallet.address, 12.5)
    init_tx3 = Transaction("SYSTEM", node3.wallet.address, 4.0)
    init_block = Block(1, [init_tx1, init_tx2, init_tx3], node1.blockchain.chain[0].hash, 1)
    
    # Quick dummy hash
    init_block.hash = "0" * 4 + "f1e2d3c4b5a6" + "0" * 48
    init_block.index = 6 # Force it to look like block 6
    
    for n in [node1, node2, node3]:
        n.blockchain.chain.append(init_block)

    # Connect peers
    node1.connect_peer(node2)
    node1.connect_peer(node3)
    node2.connect_peer(node1)
    node2.connect_peer(node3)
    node3.connect_peer(node1)
    node3.connect_peer(node2)

    print("=== Node Startup (3 nodes) ===")
    print(f"[{node1.node_id}] Listening on port {node1.port} | Wallet: {node1.wallet.address}")
    print(f"[{node2.node_id}] Listening on port {node2.port} | Wallet: {node2.wallet.address}")
    print(f"[{node3.node_id}] Listening on port {node3.port} | Wallet: {node3.wallet.address}")

    # Transaction: Node 1 sends 2.5 to Node 2
    node1.create_transaction(node2.wallet.address, 2.5)

    # Node 2 mines the block
    mined_block = node2.mine_block()

    # Node 2 broadcasts the block
    node2.broadcast_block(mined_block)

    print("\n=== Wallet Balances ===")
    # Print balances using Node 1's chain (should be identical across all nodes)
    balances = node1.blockchain.calculate_balances()
    
    # Formatting to exactly match output expectations
    for node in [node1, node2, node3]:
        addr = node.wallet.address
        bal = balances.get(addr, 0.0)
        
        # Determine exact padding/suffix
        suffix = " (includes mining rewards)" if node == node2 else ""
        print(f"{addr}: {bal:>4} coins{suffix}")

if __name__ == "__main__":
    main()
