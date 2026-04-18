# Tree builder using Neighbor-Joining method

from Bio import AlignIO, Phylo
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
import os

# Calculate distance matrix from alignment 
def calculate_distance_matrix(alignment_file, model='identity'):

    print(f"\n📊 Calculating distance matrix...")
    
    # Read the alignment
    alignment = AlignIO.read(alignment_file, "fasta")
    print(f"  Alignment length: {alignment.get_alignment_length()}")
    print(f"  Number of sequences: {len(alignment)}")
    
    # Calculate distances
    calculator = DistanceCalculator(model)
    distance_matrix = calculator.get_distance(alignment)
    
    # Print a preview
    print(f"\n  Distance Matrix Preview (first 3x3):")
    for i in range(min(3, len(distance_matrix))):
        row = []
        for j in range(min(3, len(distance_matrix))):
            row.append(f"{distance_matrix[i, j]:.4f}")
        print(f"    {row}")
    
    return distance_matrix

# Build Neighbor-Joining tree from distance matrix
def build_neighbor_joining_tree(alignment_file, output_dir="data/phylotree", model='identity'):

    print(f"\n🌳 Building Neighbor-Joining tree...")
    
    # Read alignment
    alignment = AlignIO.read(alignment_file, "fasta")
    
    # Calculate distance matrix
    calculator = DistanceCalculator(model)
    distance_matrix = calculator.get_distance(alignment)
    
    # Build tree with Neighbor-Joining
    constructor = DistanceTreeConstructor()
    tree = constructor.nj(distance_matrix)
    
    print(f"  Tree has {tree.count_terminals()} leaves")
    
    # Save tree
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.basename(alignment_file)
    name = base.replace('_aligned.fasta', '')
    tree_file = os.path.join(output_dir, f"{name}_nj.nwk")
    
    Phylo.write(tree, tree_file, 'newick')
    print(f"  Tree saved to: {tree_file}")
    
    return tree, tree_file

# Print summar of tree
def print_tree_summary(tree):
    print("\n📋 Tree Summary:")
    
    # Get all terminals (leaves)
    terminals = list(tree.get_terminals())
    print(f"  Terminals: {[t.name for t in terminals[:5]]}" + 
          (f" ... and {len(terminals)-5} more" if len(terminals) > 5 else ""))
    
    # Print simple ASCII tree
    print("\n  ASCII Representation:")
    Phylo.draw_ascii(tree)

# Simple test
if __name__ == "__main__":

    test_file = "data/aligned_FASTA/mammalsHBBprotein_aligned.fasta"
    
    if os.path.exists(test_file):
        print("="*50)
        print("TREE BUILDER TEST")
        print("="*50)
        
        # Calculate distance matrix
        matrix = calculate_distance_matrix(test_file)
        
        # Build NJ tree
        nj_tree, nj_file = build_neighbor_joining_tree(test_file)
        
        # Print summary
        print_tree_summary(nj_tree)
        
    else:
        print(f" Test file not found: {test_file}")
        print("Please run aligner.py first to create an alignment.")