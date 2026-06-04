from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np



model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
embeddings = model.encode(cleaned_chunk) #chunks of the data
#print(embeddings)
#for i in embeddings:
   # i.flatten()
    #print(embeddings)



def search(query):
    query_embedding = model.encode(query)
    similarity_scores = cosine_similarity(query_embedding.reshape(1,-1), embeddings)
    for i in similarity_scores:
        new_similarity_scores =i.flatten()
    
    sorted_list = []
    #print(query_embedding)

    for chunk, scores in zip(cleaned_chunk, new_similarity_scores):
        sorted_list.append((chunk, scores))
    #print("Score:", scores, "chunk:", chunk)
    sorted_list.sort(key = lambda x: x[1], reverse=True)

    top = sorted_list[:3]
    return top

"""
    for chunk, score in top:
        print("chunk:", chunk, "score:", score)

"""
#print(similarity_scores)


# for checking the scores of the chunks with the query





 