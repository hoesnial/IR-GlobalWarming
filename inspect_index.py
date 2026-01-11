
import pickle
import os

index_path = r'd:\COLLAGE\dataMining\Global_Warming\data\inverted_index.pkl'

if os.path.exists(index_path):
    with open(index_path, 'rb') as f:
        data = pickle.load(f)
    
    docs = data['documents']
    print(f"Total documents in index: {len(docs)}")
    
    print("\nSample Documents Metadata:")
    for i, (doc_id, doc) in enumerate(list(docs.items())[:5]):
        print(f"ID: {doc_id}")
        print(f"Title: {doc.get('title', 'No Title')}")
        print(f"PDF Path: {doc.get('pdf_path', 'N/A')}")
        print(f"Source File: {doc.get('source_file', 'N/A')}")
        print("-" * 50)
else:
    print("Index file not found!")
