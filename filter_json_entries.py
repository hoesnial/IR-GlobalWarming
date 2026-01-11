import json
import os
import re

def clean_filename(title):
    # Logic copied from DocumentDownloader
    clean = re.sub(r'[\\/*?:"<>|]', "", title)
    clean = clean[:100]
    return clean.strip()

def filter_json():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    json_path = os.path.join(data_dir, 'documents.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)
        
    filtered_docs = []
    removed_count = 0
    
    for doc in documents:
        title = doc.get('title', '')
        # Construct filename based on title as the downloader did
        filename = clean_filename(title) + ".pdf"
        filepath = os.path.join(data_dir, filename)
        
        # Check if PDF file exists
        if os.path.exists(filepath):
            filtered_docs.append(doc)
        else:
            removed_count += 1
            print(f"Removing entry: {title} (No PDF found)")
        
    # Save back
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_docs, f, indent=4, ensure_ascii=False)
        
    print(f"\nSelesai! {removed_count} entri tanpa file PDF telah dihapus dari JSON.")
    print(f"Tersisa {len(filtered_docs)} dokumen.")

if __name__ == "__main__":
    filter_json()
