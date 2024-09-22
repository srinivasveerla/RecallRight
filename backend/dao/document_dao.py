import chromadb
from models.document import Document

class DocumentDao:

    def __init__(self, path) -> None:
        client = chromadb.PersistentClient(path = path)
        self.tag_db = client.get_or_create_collection(name="tag_collection",metadata={"hnsw:space": "cosine"})        
        self.content_db = client.get_or_create_collection(name="content_collection",metadata={"hnsw:space": "cosine"})


    def retrieve_similar(self, db, query, threshold=0.3, n_results=100):
        """Takes in a query text and returns a filtered list of docs based on threshold."""
        results = db.query(query_texts=[query], n_results=n_results)
        
        # Extract the distances and corresponding metadata
        filtered_results = {
            'ids': [],
            'distances': [],
            'metadatas': [],
            'documents': []
        }

        for ind, dist in enumerate(results['distances'][0]):
            if dist < threshold:
                filtered_results['ids'].append(results['ids'][0][ind])
                filtered_results['distances'].append(dist)
                filtered_results['metadatas'].append(results['metadatas'][0][ind])
                filtered_results['documents'].append(results['documents'][0][ind])
        
        # Return the filtered results if any match, else return None
        if filtered_results['ids']:
            return filtered_results
        else:
            return None
        

    def retrieve_by_tags(self, query, n_results=100):
        return self.retrieve_similar(self.tags_db, query, n_results)
    
    def retrieve_by_content(self, query, n_results=100, threshold = 0.3):
        return self.retrieve_similar(self.content_db, query, threshold, n_results)

    def store_document(self, document: Document):
        self.tag_db.add(documents = document.tags, ids=document.ids, metadatas = document.tags_metadata)
        self.content_db.add(documents = document.content, ids=document.ids, metadatas = document.content_metadata)
        
    def remove_document(self, ids):
        self.content_db.delete(ids = ids)
        self.tag_db.delete(ids = ids)

    def get_tags(self):
        all_embeddings = self.content_db.get(include=['metadatas'])
        all_tags = [item.get('tags') for item in all_embeddings['metadatas'] if 'tags' in item]
        return all_tags