from flask import Flask, request, jsonify
from nltk.corpus import wordnet
from sklearn.metrics import pairwise_distances
import pickle
from nltk.metrics import edit_distance
from Indexer import Indexer

app = Flask(__name__)

# Load the pre-built index


indexer = Indexer()
LIMIT = 5


# Read the content of the document
with open("output.json", "r") as f:
    document_content = f.read()


# Later, in another script or session:
indexer = Indexer()
indexer.load_index("index.pkl")
indexer.add_document(document_content)


@app.route('/query', methods=['POST'])
def query_processor():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Invalid request. Missing query parameter.'}), 400

    query = data['query']
    corrected_query = correct_spelling(query)
    results = execute_query(corrected_query)

    return jsonify({'results': results})


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Invalid request. Missing query parameter.'}), 400

    corrected_query = correct_spelling(query)
    results = execute_query(corrected_query)

    return jsonify({'results': results,
                    "query": query,
                    "corrected_query": corrected_query})


@app.route('/')
def home():
    return '''
    <h1>Search Engine</h1>
    <form method="get" action="/search">
        <label for="query">Enter your query:</label><br>
        <input type="text" id="query" name="query"><br>
        <input type="submit" value="Submit">
    </form>
    '''


def correct_spelling(query):
    corrected_query = []
    for word in query.split():
        if not wordnet.synsets(word):
            # If the word is not found in WordNet, attempt to correct it
            closest_word = min(
                wordnet.words(), key=lambda w: edit_distance(word, w))
            corrected_query.append(closest_word)
        else:
            corrected_query.append(word)
    return ' '.join(corrected_query)


def execute_query(query):
    # Tokenize the query
    tokens = query.split()

    # Perform query expansion using WordNet synonyms
    expanded_query = expand_query(tokens)

    # Execute the expanded query against the index
    results = indexer.search(expanded_query, top_k=LIMIT)

    return results


def expand_query(tokens):
    expanded_tokens = []
    for token in tokens:
        # For each token, find synonyms using WordNet
        synonyms = set()
        for syn in wordnet.synsets(token):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())
        # Add original token and synonyms to the expanded query
        expanded_tokens.extend([token] + list(synonyms))
    # Combine expanded tokens into a single string
    expanded_query = ' '.join(expanded_tokens)
    return expanded_query


if __name__ == '__main__':
    app.run(debug=True)
