import json
import os
import re

def clean_filename(title):
    # Logic copied from DocumentDownloader
    clean = re.sub(r'[\\/*?:"<>|]', "", title)
    clean = clean[:100]
    return clean.strip()

def update_json():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    json_path = os.path.join(data_dir, 'documents.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)
        
    updated_docs = []
    removed_count = 0
    
    for doc in documents:
        title = doc.get('title', '')
        filename = clean_filename(title) + ".pdf"
        filepath = os.path.join(data_dir, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            # File doesn't exist (failed download), so remove the download link
            if 'download' in doc:
                del doc['download']
                removed_count += 1
        
        updated_docs.append(doc)
        
    # Save back
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(updated_docs, f, indent=4, ensure_ascii=False)
        
    print(f"Updated JSON. Removed 'download' component from {removed_count} documents.")

if __name__ == "__main__":
    update_json()
