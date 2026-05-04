RAG stands for Retrieval Augmented Generation. The flow is:

Take all the text we fetched (fundamentals + financials + news)
Chunk it into smaller pieces
Embed each chunk — convert text into numbers (vectors) that capture meaning
Store those vectors in FAISS
When user asks a question — embed the question too and find the most similar chunks
Send those relevant chunks to Claude Haiku to generate the analysis


RAG is the research assistant — goes through thousands of pages, finds the 5 most relevant paragraphs
Claude Haiku is the senior analyst — reads those 5 paragraphs and writes the investment report