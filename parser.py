# FASTA parsing Functions
from Bio import SeqIO
import os

def read_fasta(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    records = list(SeqIO.parse(file_path, "fasta"))
    print(f"Read {len(records)} sequences from {file_path}")
    return records

# Extracts species names from description
def extract_species(record):

    description = record.description

    # Case1: [Homo sapiens] format
    if '[' in description and ']' in description:
        start = description.find('[') + 1
        end = description.find(']')
        if start > 0 and end > start:
            return description[start:end]
    
    # Case2: OS=Homo sapiens (UniProt format)
    if 'OS=' in description:
        parts = description.split('OS=')
        if len(parts) > 1:
            species_part = parts[1].split('GN=')[0].strip()
            return species_part
    
    # Case3: Just use the ID
    return record.id

# Prints a summary of the FASTA file
def summarize_fasta(file_path):
    records = read_fasta(file_path)
    
    print(f"FASTA Summary:")
    
    for i, record in enumerate(records):
        species = extract_species(record)
        print(f"\n{i+1}. ID: {record.id}")
        print(f"   Species: {species}")
        print(f"   Length: {len(record.seq)}")
        print(f"   Preview: {str(record.seq)[:50]}...")
    
    return records

# Test Module
if __name__ == "__main__":
    test_file = "data/input/HBB_protein.fasta"
    if os.path.exists(test_file):
        summarize_fasta(test_file)
    else:
        print(f"Test file not found. Please create {test_file}")