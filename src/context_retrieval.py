import torch
from sentence_transformers import SentenceTransformer, util
from download_embeddings import load_embeddings_from_s3

# Load the embeddings from S3 directly into memory
embedding_data = load_embeddings_from_s3()

# Convert embeddings to a torch tensor and move to the appropriate device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
embeddings = torch.tensor(embedding_data['embeddings']).to(device)
chunks = embedding_data['pairs']

# Load the retrieval model and move it to the appropriate device
retrieval_model = SentenceTransformer('all-MiniLM-L6-v2')
retrieval_model = retrieval_model.to(device)

# Function to retrieve similar transcripts based on the user's input
def retrieve_similar_transcripts_chain(prompt):
    # Encode the user's prompt to the same device as embeddings
    user_embedding = retrieval_model.encode(prompt, convert_to_tensor=True).to(device)
    # Calculate cosine similarities between the user's embedding and the stored embeddings
    similarities = util.pytorch_cos_sim(user_embedding, embeddings)[0]
    # Get the top 2 most similar responses
    top_indices = torch.topk(similarities, k=2).indices.tolist()

    # Prepare the retrieved context with the corresponding counselor messages
    results = []
    scores_cpu = similarities.cpu().numpy()
    for idx in top_indices:
        if idx >= len(chunks):
            continue
        client_message, counselor_message = chunks[idx]
        results.append({
            'client': client_message.strip(),
            'counselor': counselor_message.strip(),
            'score': scores_cpu[idx]
        })

    # Compile the retrieved context into a structured format
    retrieved_context = "Incorporate the following real-life examples into your responses to make them more relatable and human-like, ensuring they align with the user's current situation:\n"
    for transcript in results:
        retrieved_context += f"(Client): {transcript['client']}\n"
        retrieved_context += f"(Counselor): {transcript['counselor']}\n\n"

    return retrieved_context