<h1>Agentic RAG (Retrieval Augmented Generation) with LangChain and Supabase</h1>

<h2>Prerequisites</h2>
<ul>
  <li>Python 3.11+</li>
</ul>

<h2>Installation</h2>
<h3>1. Clone the repo</h3>

```
git clone https://github.com/seancondron/advanced-agentic-rag-chatbot.git
cd Agentic RAG with LangChain
```

<h3>2. Create a virtual environment</h3>

```
python -m venv venv
```

<h3>3. Activate the virtual environment</h3>

```
Windows:venv\Scripts\Activate
Mac: source venv/bin/activate
```

<h3>4. Install dependencies</h3>

```
pip install -r requirements.txt
```

<h3>5. Source Supabase and OpenAI API Keys</h3>

- Create a free account on Supabase: https://supabase.com/
- Create an API key for OpenAI: https://platform.openai.com/api-keys

<h3>6. Execute SQL queries in Supabase</h3>

Execute the following SQL query in the Supabase:

```
-- Enable pgvector extension to work with embedding vectors
create extension if not exists vector;

-- Create table to store documents
create table
  documents (
    id uuid primary key,
    content text, -- corresponds to Document.pageContent
    metadata jsonb, -- corresponds to Document.metadata
    embedding vector (1536) -- 1536 works for OpenAI embeddings, change if needed
  );

-- Create function to search for documents
create function match_documents (
  query_embedding vector (1536),
  filter jsonb default '{}'
) returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
) language plpgsql as $$
#variable_conflict use_column
begin
  return query
  select
    id,
    content,
    metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where metadata @> filter
  order by documents.embedding <=> query_embedding;
end;
$$;
```

<h3>7. Add API keys to .env file</h3>

- Add the API keys for Supabase and OpenAI to the .env file


<h3>8. Add your documents for LLM to reference</h3>

- Add the documents you want the LLM to reference in 'documents' folder

<h3>9. Execute the scripts</h2>

- Open terminal
- Execute the following commands:

```
python ingest_in_db.py
python agentic_rag.py
streamlit run agentic_rag_streamlit.py
```
