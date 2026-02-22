import os
import subprocess
from Bio import SeqIO, AlignIO
from parser import extract_species

def align_file(input_path, output_dir="data/output"):
    
    os.makedirs(output_dir, exist_ok=True)

    # Set output path
    base = os.path.basename(input_path)
    name = os.path.splitext(base)[0]
    output_path = os.path.join(output_dir, f"{name}_aligned.fasta")
    
    # Read input file
    seqs = list(SeqIO.parse(input_path, "fasta"))
    print(f"Aligning {len(seqs)} sequences...")
    
    # Run MUSCLE
    cmd = ["muscle.exe", "-align", input_path, "-output", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"Aligned file saved to: {output_path}")
        
        # Print a preview
        aligned = AlignIO.read(output_path, "fasta")
        for i, rec in enumerate(aligned, 1):
            species = extract_species(seqs[i-1])
            print(f"  {i}. {species[:15]}: {str(rec.seq)[:30]}...")
        
        return output_path
    else:
        print(f"Failed")
        return None


# Test aligner
if __name__ == "__main__":
    
    test_file = "data/input/HBB_protein.fasta"
    if os.path.exists(test_file):
        align_file(test_file)
    else:
        print(f"Place your FASTA file in: data/input/")