from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle


class Indexer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.documents = []

    def add_document(self, doc_text):
        self.documents.append(doc_text)

    def build_index(self):
        self.vectorizer.fit(self.documents)

    def save_index(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.vectorizer, f)

    def load_index(self, filename):
        with open(filename, 'rb') as f:
            self.vectorizer = pickle.load(f)

    def search(self, query, top_k=10):
        if not self.vectorizer.vocabulary_:
            raise ValueError("Index is not built. Call build_index() first.")

        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(
            query_vector, self.vectorizer.transform(self.documents))

        # Get the top-k most similar documents
        top_k_indices = similarities.argsort()[0][-top_k:][::-1]
        results = [(self.documents[i], similarities[0, i])
                   for i in top_k_indices]
        return results


# Usage:
indexer = Indexer()

# Read the content of the document
with open("output.json", "r") as f:
    document_content = f.read()

# Add the document content to the indexer
indexer.add_document(document_content)
indexer.build_index()
indexer.save_index("index.pkl")

# Later, in another script or session:
indexer = Indexer()
indexer.load_index("index.pkl")
indexer.add_document(document_content)
results = indexer.search("bussiness", top_k=5)
for doc, score in results:
    print(f"Document: {doc}, Score: {score}")
