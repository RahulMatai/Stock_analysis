Imagine you're a financial analyst.
Your boss says "Give me a full report on Reliance Industries by evening."
You don't know everything about Reliance from memory. So you:

Gather documents — you collect Reliance's financial statements, news articles, key numbers. That's our prepare_text() — collecting all data in one place.
Organize them — you don't read everything at once. You split documents into smaller sections and put sticky notes on each. That's our chunk_text() — breaking data into 34 manageable pieces.
Index them — you arrange those sections by topic so you can find them fast. That's our create_vector_store() — storing all chunks as vectors in FAISS so they're searchable by meaning.
Answer a question — your boss asks "Is Reliance profitable?" You don't re-read everything. You go straight to the relevant sticky note sections. That's our search_vectorstore() — finding the top 3 most relevant chunks instantly.
Write the report — you hand those relevant sections to the senior analyst who writes the final report. That's Claude Haiku in the next step — reading the relevant chunks and generating the analysis.


RAG in one line:

Instead of making the AI memorize everything, we teach it to find the right information first, then answer.

That's it. rag_pipeline.py is the librarian. Claude is the analyst. Together they make FinSight AI. 🎯
