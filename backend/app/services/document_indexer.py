"""Document indexing service for building vector database."""
import os
import chromadb
from pypdf import PdfReader

from app.core.config import settings


chroma_client = chromadb.PersistentClient(path=str(settings.EMBEDDINGS_DIR))
collection_name = settings.CHROMA_COLLECTION_NAME
collection = chroma_client.get_or_create_collection(name=collection_name)


def load_pdf_documents(directory_path=None):
    """Load all PDF documents from the specified directory."""
    if directory_path is None:
        directory_path = settings.DOCUMENTS_DIR
    
    documents = []
    
    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return documents
    
    pdf_files = [f for f in os.listdir(directory_path) if f.endswith(".pdf")]
    
    if not pdf_files:
        print(f"No PDF files found in {directory_path}")
        return documents
    
    print(f"Found {len(pdf_files)} PDF files")
    
    for file_name in pdf_files:
        file_path = os.path.join(directory_path, file_name)
        try:
            reader = PdfReader(file_path)
            text = "".join(page.extract_text() for page in reader.pages)
            
            if text.strip():
                documents.append({
                    "id": file_name,
                    "text": text,
                    "source": file_name
                })
                print(f"Loaded: {file_name} ({len(text)} characters)")
            else:
                print(f"Skipped: {file_name} (empty content)")
                
        except Exception as e:
            print(f"Error reading {file_name}: {e}")
    
    return documents


def chunk_text(text, chunk_size=None, chunk_overlap=None):
    """Split text into overlapping chunks."""
    if chunk_size is None:
        chunk_size = settings.CHUNK_SIZE
    if chunk_overlap is None:
        chunk_overlap = settings.CHUNK_OVERLAP
        
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()
        
        if chunk:
            chunks.append(chunk)
        
        if end >= text_length:
            break
            
        start = end - chunk_overlap
    
    return chunks


def index_documents(documents, batch_size=100):
    """Chunk documents and store them in ChromaDB with batch processing."""
    if not documents:
        print("No documents to index")
        return
    
    print(f"\nIndexing {len(documents)} documents...")
    
    all_chunks = []
    
    for doc in documents:
        chunks = chunk_text(doc["text"])
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc['id']}_chunk_{i}"
            all_chunks.append({
                "id": chunk_id,
                "text": chunk,
                "source": doc["source"]
            })
    
    print(f"Created {len(all_chunks)} chunks")
    
    total_batches = (len(all_chunks) + batch_size - 1) // batch_size
    
    for batch_idx in range(0, len(all_chunks), batch_size):
        batch = all_chunks[batch_idx:batch_idx + batch_size]
        
        ids = [chunk["id"] for chunk in batch]
        texts = [chunk["text"] for chunk in batch]
        metadatas = [{"source": chunk["source"]} for chunk in batch]
        
        collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        
        current_batch = (batch_idx // batch_size) + 1
        print(f"Processed batch {current_batch}/{total_batches}")
    
    print(f"\nSuccessfully indexed {len(all_chunks)} chunks")


def main():
    """Main function to run the document indexing process."""
    print("Starting document indexing process...")
    print("=" * 50)
    
    documents = load_pdf_documents()
    
    if not documents:
        print("No documents loaded. Exiting.")
        return
    
    index_documents(documents)
    
    print("=" * 50)
    print("Indexing complete!")


if __name__ == "__main__":
    main()
