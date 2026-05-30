# AI Agents — Concepts

## LLM kya hai?

LLM (Large Language Model) ek neural network hai jo text predict karta hai. Tum kuch likho, wo agla token (word ya word-piece) predict karta hai. Examples: GPT-4, Claude, Llama, Gemini.

LLM khud kuch karta nahi — sirf text generate karta hai. Agar tumhe weather chahiye, LLM weather nahi laa sakta — usse koi "tool" chahiye jo actually weather API call kare.

## Agent kya hai?

Agent matlab LLM + tools + loop. Pattern simple hai:

1. User kuch puchhta hai
2. LLM decide karta hai — directly answer du, ya pehle koi tool call karu?
3. Agar tool chahiye, LLM tool ka naam + arguments deta hai
4. Agent code tool ko run karta hai
5. Tool ka result wapas LLM ko deta hai
6. LLM ab final answer banata hai

Ye loop multiple turns chal sakta hai agar ek ke baad ek tools chahiye.

## Tools kya hote hain?

Tool ek normal Python function hai jise LLM call kar sakta hai. Example:

```python
def get_weather(city: str) -> str:
    return f"Weather in {city}: 28°C"
```

LLM ko ek **schema** dete hain jisme tool ka naam, description, aur arguments ka format hota hai. LLM is schema ko padhke decide karta hai kab tool use karna hai.

## RAG kya hai?

RAG = Retrieval Augmented Generation. Idea ye hai: LLM ke paas saara knowledge nahi hota (especially tumhare private docs ka). To pehle relevant info dhundo, fir LLM ko context me do.

Steps:
1. **Documents** ko chunks me todo (chhote pieces, ~500 chars)
2. Har chunk ko **embedding** me convert karo (text → numbers vector)
3. Vectors ko **store** karo (in-memory list ya vector database me)
4. Jab user query aaye, query ko bhi embed karo
5. **Cosine similarity** se top-k matching chunks dhundo
6. Wo chunks LLM ko prompt me dedo, fir LLM answer banayega

RAG isliye useful hai kyunki LLM unlimited context nahi le sakta — sirf relevant cheezein dena better hai.

## Embeddings kya hain?

Embedding text ka numerical representation hai. Similar meaning waale texts ke vectors close hote hain mathematically.

Example:
- "I love coding" → [0.2, -0.5, 0.8, ...]
- "Programming is fun" → [0.18, -0.48, 0.79, ...]  (similar)
- "Dog ate my food" → [-0.7, 0.2, -0.3, ...]   (different)

Embedding models alag hote hain LLMs se — woh specifically text similarity ke liye trained hote hain.

## Memory

Agent ko conversation yaad rakhna padta hai. Simplest way: ek list me saari messages store karo. Har LLM call pe puri list bhejo.

Bigger conversations ke liye summarization ya selective retention techniques use hote hain — but starting ke liye full list theek hai.

## Multi-tool calls

Modern LLMs ek hi turn me kai tools call kar sakte hain. Example: "what time is it and what's 5*5?" pe LLM dono `get_current_time` aur `calculate` ek saath request kar sakta hai — efficient.

Agent code ko ye handle karna padta hai — saare tool calls execute karo, saare results LLM ko ek saath wapas do.
