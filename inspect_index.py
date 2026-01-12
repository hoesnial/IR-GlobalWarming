
import pickle
import os

index_path = r'd:\COLLAGE\dataMining\Global_Warming\data\inverted_index.pkl'

if os.path.exists(index_path):
    with open(index_path, 'rb') as f:
        data = pickle.load(f)
    
    docs = data['documents']
    print(f"Total documents in index: {len(docs)}")
    
    index = data['index']
    print(f"\nTotal Unique Terms: {len(index)}")
    
    print("\nSample Inverted Index (First 10 terms):")
    print("Format: Term -> [(DocID, Freq), ...]")
    print("-" * 50)
    
    # Sort terms by frequency (posting list length) for more interesting results
    sorted_terms = sorted(index.items(), key=lambda x: len(x[1]), reverse=True)
    
    for term, postings in sorted_terms[:20]:
        print(f"{term:<20} : Found in {len(postings)} docs -> {postings[:5]}...")
    print("-" * 50)
else:
    print("Index file not found!")
