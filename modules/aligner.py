# Aligner module: Uses MUSCLE to align sequences in FASTA files
import os
import subprocess
from Bio import SeqIO, AlignIO
try:
    from .parser import extract_species, read_fasta
except ImportError:
    from parser import extract_species, read_fasta

# Uses MUSCLE to align sequences in a FASTA file and saves the output
def align_file(input_path, output_dir="data/aligned_FASTA"):
    
    os.makedirs(output_dir, exist_ok=True)

    # Set output path
    base = os.path.basename(input_path)
    name = os.path.splitext(base)[0]
    output_path = os.path.join(output_dir, f"{name}_aligned.fasta")
    
    # Read input file
    seqs = read_fasta(input_path)
    
    # Run MUSCLE
    muscle_cmd = "muscle" if os.name != 'nt' else "muscle.exe"
    cmd = [muscle_cmd, "-align", input_path, "-output", output_path]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print(f"Aligned file saved to: {output_path}")
            
            # Print a preview
            aligned = AlignIO.read(output_path, "fasta")
            for i, rec in enumerate(aligned, 1):
                if i <= 5:  # Show first 5 only
                    species = extract_species(seqs[i-1])
                    print(f"  {i}. {species[:15]}: {str(rec.seq)[:30]}...")
            if len(aligned) > 5:
                print(f"  ... and {len(aligned)-5} more sequences")
            
            return output_path
        else:
            print(f"Alignment failed: {result.stderr}")
            return None
    except FileNotFoundError:
        print("MUSCLE not found. Please ensure MUSCLE is installed and in PATH")
        return None
    except Exception as e:
        print(f"Error during alignment: {str(e)}")
        return None


# Test aligner
if __name__ == "__main__":
    
    test_file = "data/test_FASTA/vertebratesCYCSproteins.fasta"
    if os.path.exists(test_file):
        align_file(test_file)
    else:
        print(f"Place your FASTA file in: data/test_FASTA/")