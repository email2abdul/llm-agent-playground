# llm-agent-playground

Beginner-friendly tool-using LLM agent. Ek hi codebase me **Groq (Llama-4)** aur **Anthropic (Claude)** — ek variable se switch kar sakte ho.

Sikhna ke liye banaya gaya — pure Python, no frameworks (LangChain etc. nahi).

---

## Kya hai isme

- **Agent loop** — LLM tool call kare → tool run ho → result wapas LLM ko jaaye → final answer
- **Memory** — poori conversation history yaad rakhta hai
- **Tools** — `get_current_time`, `calculate` (math, `^` power bhi), `search_docs` (RAG)
- **RAG** — apne `docs/` folder ke files me semantic search (Gemini embeddings + in-memory cosine similarity)
- **Multi-provider** — Anthropic Claude ya Groq Llama-4, UI ya code se runtime pe switch
- **Web UI** — Streamlit chat interface with sidebar (provider switch, reset, tool call visibility)
- **CLI** — terminal me bhi chala sakte ho
- **Safety** — max iterations limit, Groq tool-call retry logic
- **System prompt** — agent ki personality (Guru), language rules, tool-use rules

---

## Setup

1. Repo clone karo:
   ```bash
   git clone https://github.com/email2abdul/llm-agent-playground.git
   cd llm-agent-playground
   ```

2. Dependencies install:
   ```bash
   python3 -m pip install python-dotenv groq anthropic google-genai numpy streamlit
   ```

3. Project root me `.env` file banao:
   ```
   GROQ_API_KEY=your_groq_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   GEMINI_API_KEY=your_gemini_key_here
   ```

   Keys yahan se milengi:
   - Groq → https://console.groq.com
   - Anthropic → https://console.anthropic.com
   - Gemini → https://aistudio.google.com/apikey

---

## Chalao

### Option 1: Web UI (recommended)

```bash
python3 -m streamlit run app.py
```

Browser khulega `http://localhost:8501` pe. Features:
- Chat interface (ChatGPT jaisa look)
- Left sidebar: Provider switch (Anthropic/Groq), Reset button
- Har response ke neeche **"Tool calls"** expander — kaunse tools call hue dekh sakte ho

### Option 2: Terminal (CLI)

```bash
python3 agent.py
```

Sample session:
```
Aap: 25*4 kitna hai aur abhi time kya hai?
  [Tool called: calculate(25*4)]
  [Tool called: get_current_time]
Guru: 25 * 4 = 100. Abhi time hai 1:37 PM, Saturday, May 30, 2026.
```

CLI commands:
- `exit` — agent band karne ke liye
- `reset` — conversation memory clear karne ke liye

---

## Provider switch

**UI me:** Sidebar ke "Provider" dropdown se select karo — conversation auto-reset ho jaayegi.

**Code me:** `agent.py` ke top me default badlo:

```python
PROVIDER = "anthropic"  # ya "groq"
```

| Provider | Model | Speed | Cost |
|---|---|---|---|
| `groq` | Llama-4 Scout 17B | Bahut fast | Free tier |
| `anthropic` | Claude Haiku 4.5 | Fast | Paid (sasta) |

Quality chahiye to `agent.py` me `MODEL = "claude-sonnet-4-6"` kar do.

---

## RAG — apne documents pe agent chala

Agent ke paas ab `search_docs` tool hai jo `docs/` folder ke files me semantic search karta hai.

**Use kaise karein:**

1. Apne notes/text files (`.md` ya `.txt`) `docs/` folder me daalo
2. Index banao (har baar docs change ho to chalao):
   ```bash
   python3 rag.py index
   ```
3. Agent chalao aur apne docs ke baare me puchho:
   ```
   Aap: mere notes ke according RAG kya hai?
     [Tool called: search_docs('RAG kya hai')]
   Guru: Mere docs ke according, RAG = Retrieval Augmented Generation hai...
   ```

**CLI search test** (agent ke bina):
```bash
python3 rag.py search "python list methods"
```

**Andar kya ho raha hai:**
1. Docs ko 500-char chunks me toda (100-char overlap)
2. Gemini `gemini-embedding-001` se har chunk ko 3072-dim vector banaya
3. `rag_index.pkl` me save (gitignored, regenerable)
4. Query time pe: query embed → cosine similarity → top-3 chunks return
5. Agent un chunks ko context ki tarah use karke answer banata hai

Sample docs (`python_basics.md`, `ai_agents.md`) already included hain — `python3 rag.py index` chalake test kar lo.

---

## File structure

```
.
├── agent.py          # Main agent (LLM + tools + memory + loop)
├── app.py            # Streamlit web UI
├── rag.py            # RAG: chunking, embeddings, search
├── list_models.py    # Gemini ke available models list karne ka small utility
├── docs/             # Tumhare .md / .txt files (RAG corpus)
│   ├── python_basics.md
│   └── ai_agents.md
├── rag_index.pkl     # RAG index (gitignored, auto-generated)
├── .env              # API keys (gitignored — kabhi commit mat karna)
├── .gitignore
└── README.md
```

---

## Naya tool kaise add karein

1. Python function likho:
   ```python
   def get_weather(city: str) -> str:
       return f"Weather in {city}: 28°C, sunny"
   ```

2. `TOOL_FUNCTIONS` dict me register karo:
   ```python
   TOOL_FUNCTIONS = {
       "get_current_time": get_current_time,
       "calculate": calculate,
       "get_weather": get_weather,  # naya
   }
   ```

3. `TOOLS_SCHEMA_GROQ` aur `TOOLS_SCHEMA_ANTHROPIC` **dono** me uska schema add karo (formats thode alag hain).

4. Bas — LLM khud decide karega kab use karna hai.

---

## Roadmap (aage kya seekhna hai)

- [x] **RAG** — vector DB + embeddings + semantic search se documents query karna ✅
- [x] **Web UI** — Streamlit chat interface ✅
- [ ] **MCP** — tools ko external MCP server me convert karna (Anthropic ka standard)
- [ ] **ChromaDB upgrade** — in-memory ki jagah proper persistent vector DB
- [ ] Streaming responses (token-by-token output)
- [ ] More tools (web search, file ops, code execution)
- [ ] Conversation persistence (file/DB me save karo)

---

## Concepts jo cover hue

- LLM API calls (Groq, Anthropic, Gemini embeddings)
- Function/tool calling
- Agent loop (multi-turn tool use)
- Conversation memory
- System prompts
- Multi-provider abstraction
- API key management (`.env` + `python-dotenv`)
- **RAG** — chunking, embeddings, cosine similarity, retrieval
- Tool-based RAG integration (LLM khud decide karta hai kab docs search karna hai)
