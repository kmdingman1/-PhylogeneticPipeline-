# Compares MUSCLE alignment with T-Coffee reference
from Bio import AlignIO, SeqIO

def compare_alignments(muscle_file, tcoffee_file, original_file):
    """Compare MUSCLE alignment with T-Coffee reference"""
    
    print("="*60)
    print("MUSCLE vs T-COFFEE COMPARISON")
    print("="*60)
    
    # Read files
    muscle = AlignIO.read(muscle_file, "fasta")
    tcoffee = AlignIO.read(tcoffee_file, "fasta")
    original = {r.id: r for r in SeqIO.parse(original_file, "fasta")}
    
    # Basic info
    print(f"\nMUSCLE length: {muscle.get_alignment_length()}")
    print(f"T-Coffee length: {tcoffee.get_alignment_length()}")
    print(f"Sequences: {len(muscle)}")
    
    # Check if alignments ahve the same length
    if muscle.get_alignment_length() != tcoffee.get_alignment_length():
        print("\n  WARNING: Alignments have different lengths!")
        print(f"   This may affect the comparison accuracy")

    # Check IDs match
    muscle_ids = {r.id for r in muscle}
    tcoffee_ids = {r.id for r in tcoffee}
    
    if muscle_ids != tcoffee_ids:
        print("\n Sequence IDs don't match")
        return
    
    print("\n All sequences match")
    
    # Compare each sequence
    print("\n" + "-"*60)
    print(f"{'ID':20} {'Identity':10} {'MUSCLE gaps':12} {'T-Coffee gaps':12}")
    print("-"*60)
    
    muscle_dict = {r.id: r for r in muscle}
    tcoffee_dict = {r.id: r for r in tcoffee}
    
    total_identity = 0
    
    for seq_id in sorted(muscle_ids):
        m_seq = str(muscle_dict[seq_id].seq)
        t_seq = str(tcoffee_dict[seq_id].seq)
        
        # Count matches and gaps
        matches = 0
        m_gaps = m_seq.count('-')
        t_gaps = t_seq.count('-')
        
        # Compare position by position
        for i in range(min(len(m_seq), len(t_seq))):
            if m_seq[i] == t_seq[i]:
                matches += 1
        
        identity = (matches / min(len(m_seq), len(t_seq))) * 100
        total_identity += identity
        
        print(f"{seq_id[:20]:20} {identity:6.1f}%     {m_gaps:4d}           {t_gaps:4d}")
    
    # Summary
    avg_identity = total_identity / len(muscle_ids)
    
    print("\n" + "="*60)
    print(f"AVERAGE IDENTITY: {avg_identity:.1f}%")
    
    if avg_identity > 95:
        print("Great match - alignments are nearly identical")
    elif avg_identity > 85:
        print("Good agreement - minor differences")
    else:
        print("Noticeable differences - check data")
    
    # Show first few differences
    first_id = sorted(muscle_ids)[0]
    m_seq = str(muscle_dict[first_id].seq)
    t_seq = str(tcoffee_dict[first_id].seq)
    
    print(f"\nFirst 50 positions of {first_id}:")
    print(f"MUSCLE:  {m_seq[:50]}")
    print(f"T-Coffee: {t_seq[:50]}")
    
    # Show where they differ
    diffs = []
    for i in range(min(50, len(m_seq), len(t_seq))):
        if m_seq[i] != t_seq[i]:
            diffs.append(i)
    
    if diffs:
        print(f"\nDifferences at positions: {diffs[:10]}")


if __name__ == "__main__":
    compare_alignments(
        muscle_file="data/aligned_FASTA/vertebratesCYCSprotein_aligned.fasta",
        tcoffee_file="data/reference/CYCSprotein_tcoffee_aligned.fasta",
        original_file="data/test_FASTA/vertebratesCYCSprotein.fasta"
    )