# llm-agent-playground

Beginner-friendly tool-using LLM agent. Ek hi codebase me **Groq (Llama-4)** aur **Anthropic (Claude)** — ek variable se switch kar sakte ho.

Sikhna ke liye banaya gaya — pure Python, no frameworks (LangChain etc. nahi).

---

## Kya hai isme

- **Agent loop** — LLM tool call kare → tool run ho → result wapas LLM ko jaaye → final answer
- **Memory** — poori conversation history yaad rakhta hai
- **Tools** — `get_current_time` aur `calculate` (math evaluator, `^` power bhi)
- **Multi-provider** — `PROVIDER = "groq"` ya `"anthropic"` line badlo, baki kuch change nahi
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
   python3 -m pip install python-dotenv groq anthropic google-genai
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

Commands:
- `exit` — agent band karne ke liye
- `reset` — conversation memory clear karne ke liye

---

## Provider switch

`agent.py` ke top me PROVIDER badlo:

```python
PROVIDER = "anthropic"  # ya "groq"
```

| Provider | Model | Speed | Cost |
|---|---|---|---|
| `groq` | Llama-4 Scout 17B | Bahut fast | Free tier |
| `anthropic` | Claude Haiku 4.5 | Fast | Paid (sasta) |

Quality chahiye to `agent.py` me `MODEL = "claude-sonnet-4-6"` kar do.

---

## File structure

```
.
├── agent.py          # Main agent (LLM + tools + memory + loop)
├── list_models.py    # Gemini ke available models list karne ka small utility
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

- [ ] **RAG** — vector DB + embeddings + semantic search se documents query karna
- [ ] **MCP** — tools ko external MCP server me convert karna (Anthropic ka standard)
- [ ] Streaming responses (token-by-token output)
- [ ] More tools (web search, file ops, code execution)
- [ ] Conversation persistence (file/DB me save karo)

---

## Concepts jo cover hue

- LLM API calls (Groq, Anthropic)
- Function/tool calling
- Agent loop (multi-turn tool use)
- Conversation memory
- System prompts
- Multi-provider abstraction
- API key management (`.env` + `python-dotenv`)
