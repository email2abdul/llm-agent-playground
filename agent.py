import os
import json
from datetime import datetime
from dotenv import load_dotenv

from rag import search_docs as _rag_search

load_dotenv()

# ============================================================
# PROVIDER CHOICE — yahan badlo aur agent dusra LLM use karega
#   "groq"      → Llama-4 Scout (free, fast)
#   "anthropic" → Claude (Anthropic)
# ============================================================
PROVIDER = "anthropic"

# Provider ke hisaab se client aur model setup
if PROVIDER == "groq":
    from groq import Groq

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

elif PROVIDER == "anthropic":
    from anthropic import Anthropic

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    # Haiku 4.5 = sasta + fast, learning ke liye perfect
    # Quality chahiye to "claude-sonnet-4-6" use karo
    MODEL = "claude-haiku-4-5-20251001"

else:
    raise ValueError(f"Unknown PROVIDER '{PROVIDER}'. Use 'groq' ya 'anthropic'.")


# ============================================================
# TOOLS — Python functions (provider-independent)
# ============================================================

def get_current_time() -> str:
    """Aaj ka date aur abhi ka time return karta hai."""
    print("  🔧 [Tool called: get_current_time]")
    return datetime.now().strftime("%I:%M %p on %A, %B %d, %Y")


def calculate(expression: str) -> str:
    """Math expression evaluate karta hai. Power ke liye ^ ya ** dono chalega."""
    print(f"  🔧 [Tool called: calculate({expression})]")
    expr = expression.replace("^", "**")
    allowed = set("0123456789+-*/().%* ")
    if not all(c in allowed for c in expr):
        return f"Error: '{expression}' mein unsupported character hai. Use only: numbers, + - * / ( ) ^ **"
    try:
        return f"{expression} = {eval(expr)}"
    except Exception as e:
        return f"Calculation error: {e}"


def search_docs(query: str) -> str:
    """docs/ folder ke indexed documents me query ke relevant chunks dhundta hai (RAG)."""
    print(f"  🔧 [Tool called: search_docs({query!r})]")
    return _rag_search(query)


TOOL_FUNCTIONS = {
    "get_current_time": get_current_time,
    "calculate": calculate,
    "search_docs": search_docs,
}


# ============================================================
# TOOL SCHEMAS — dono providers ka format thoda alag hai
# ============================================================

# Groq/OpenAI format — "type":"function" wrapper + "parameters"
TOOLS_SCHEMA_GROQ = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Aaj ka date aur abhi ka time return karta hai. Use karo jab user puchhe time, date, kaun sa din, etc.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Math expression evaluate karta hai. Use karo har calculation/arithmetic ke liye.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression as string. Example: '243 * 587' or '(100+50)/3'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "User ke indexed documents (notes, tutorials, etc.) me semantic search karta hai. Use karo jab user puchhe 'docs me kya likha hai about X', 'notes ke according', 'apne documents se batao', ya koi specific concept jo user ke private docs me ho sakta hai.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query. User ka sawal as-is ya thoda rephrased. Example: 'what is RAG', 'python list methods'",
                    }
                },
                "required": ["query"],
            },
        },
    },
]

# Anthropic format — flat, "input_schema" instead of "parameters"
TOOLS_SCHEMA_ANTHROPIC = [
    {
        "name": "get_current_time",
        "description": "Aaj ka date aur abhi ka time return karta hai. Use karo jab user puchhe time, date, kaun sa din, etc.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "calculate",
        "description": "Math expression evaluate karta hai. Use karo har calculation/arithmetic ke liye.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression as string. Example: '243 * 587' or '(100+50)/3'",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "search_docs",
        "description": "User ke indexed documents (notes, tutorials, etc.) me semantic search karta hai. Use karo jab user puchhe 'docs me kya likha hai about X', 'notes ke according', 'apne documents se batao', ya koi specific concept jo user ke private docs me ho sakta hai.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query. User ka sawal as-is ya thoda rephrased. Example: 'what is RAG', 'python list methods'",
                }
            },
            "required": ["query"],
        },
    },
]


# ============================================================
# SYSTEM INSTRUCTION (same for both providers)
# ============================================================

SYSTEM_INSTRUCTION = """
You are a friendly coding teacher named 'Guru'.

LANGUAGE RULES (very important):
1. DEFAULT language: English. Reply in clean, simple English.
2. SWITCH to Hinglish (Hindi + English mix, English script) ONLY when:
   - User explicitly asks (e.g., "reply in Hinglish", "Hindi mein batao", "hinglish mein samjhao")
   - User's own message is clearly in Hinglish/Hindi
3. Once user requests Hinglish, keep using Hinglish until they ask to switch back to English.
4. When in Hinglish mode: call user 'bhai' or 'dost', call yourself 'Guru'.
5. When in English mode: use friendly but professional tone, no slang.

GENERAL RULES:
6. Keep replies short — 5-6 lines max unless user asks for detail.
7. Remember user's past info (name, location, preferences) across the conversation.
8. If the user asks MULTIPLE things in one message (e.g., "explain X and calculate Y"),
   answer EVERY part. Do not skip or forget any sub-question.
9. When you call a tool, you MUST include the tool's result in your final answer.
   Example: if calculate returns "245 * 78 = 19110", your answer must mention 19110.
   Never call a tool and then ignore its output.

TOOL USAGE — BE VERY CAREFUL:
You have THREE tools: get_current_time, calculate, search_docs. Use them ONLY for these exact cases.

CALL get_current_time when user asks about ACTUAL current time/date, like:
  - "what time is it?", "abhi time kya hai?"
  - "what's today's date?", "aaj kaun sa din hai?"

CALL calculate when user asks for ACTUAL math, like:
  - "243 * 587 kitna?"
  - "what is 15% of 1200?"
  - "calculate (100+50)/3"

CALL search_docs when user refers to their OWN documents/notes, like:
  - "docs me kya likha hai about X?"
  - "mere notes ke according RAG kya hai?"
  - "apne documents se batao Python list ke baare me"
  - "from my docs, what is an agent?"
Do NOT call search_docs for general knowledge questions you already know — only when user explicitly references their docs/notes.

CRITICAL — MULTI-PART QUESTIONS:
If user asks MULTIPLE things requiring DIFFERENT tools in one message, you MUST call ALL relevant tools.
NEVER drop any tool call. Examples:
  - "what time is it and 2^10?" → MUST call BOTH get_current_time AND calculate("2^10")
  - "current time aur 50+50 batao" → MUST call BOTH get_current_time AND calculate("50+50")
  - "docs me Python kya bola hai aur 5*5 kitna?" → BOTH search_docs AND calculate.
Plan your tool calls FIRST: list every tool needed, then call them all before answering.

DO NOT call any tool for general conceptual questions answerable from your own knowledge:
  - "function kya hota hai?" / "what is a function?" → no tool, just explain
  - "loop explain karo" → no tool, just explain
  - General definitional/explanatory question → no tool.
  - EXCEPTION: if user explicitly says "from my docs" or "mere notes ke according" → use search_docs.

If unsure whether to call a tool, DON'T call it — just answer in text.

POWER OPERATOR: For powers like 2^10 or 3^5, pass them directly as "2^10" or "3^5" to calculate.
Do NOT expand to "2*2*2..." — calculate already handles ^ for you.
"""


# ============================================================
# MEMORY — message history
# Groq mein system message list mein hota hai; Anthropic mein alag param hai.
# ============================================================

def fresh_messages():
    if PROVIDER == "groq":
        return [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    else:  # anthropic
        return []


messages = fresh_messages()


# ============================================================
# AGENT TURN — provider ke hisaab se dispatch
# ============================================================

def run_agent_turn(user_input: str, max_iterations: int = 5) -> str:
    if PROVIDER == "groq":
        return _run_groq(user_input, max_iterations)
    else:
        return _run_anthropic(user_input, max_iterations)


def _run_groq(user_input: str, max_iterations: int) -> str:
    messages.append({"role": "user", "content": user_input})

    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS_SCHEMA_GROQ,
        )
        msg = response.choices[0].message

        # No tool call → final answer
        if not msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content})
            return msg.content

        # Tool call(s) requested
        messages.append(
            {
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
            }
        )

        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments or "{}")
            fn = TOOL_FUNCTIONS.get(fn_name)
            if fn is None:
                result = f"Error: tool '{fn_name}' nahi mila"
            else:
                try:
                    result = fn(**fn_args)
                except Exception as e:
                    result = f"Tool error: {e}"
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
            )

    print(f"  ⚠️  Max {max_iterations} tool iterations cross — loop break.")
    fallback = "Sorry bhai, mujhe is question mein confusion ho gayi. Phir se try karo."
    messages.append({"role": "assistant", "content": fallback})
    return fallback


def _run_anthropic(user_input: str, max_iterations: int) -> str:
    messages.append({"role": "user", "content": user_input})

    for _ in range(max_iterations):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_INSTRUCTION,
            messages=messages,
            tools=TOOLS_SCHEMA_ANTHROPIC,
        )

        # Assistant turn ko history mein store karo (content blocks as dicts)
        assistant_blocks = [block.model_dump() for block in response.content]
        messages.append({"role": "assistant", "content": assistant_blocks})

        # Agar tool use nahi hua → final answer ready
        if response.stop_reason != "tool_use":
            text_parts = [b.text for b in response.content if b.type == "text"]
            return "\n".join(text_parts).strip()

        # Tool use blocks ko execute karo
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                fn = TOOL_FUNCTIONS.get(block.name)
                if fn is None:
                    result = f"Error: tool '{block.name}' nahi mila"
                else:
                    try:
                        result = fn(**block.input)
                    except Exception as e:
                        result = f"Tool error: {e}"
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    }
                )

        # Anthropic mein tool results ek "user" message ke andar content blocks hote hain
        messages.append({"role": "user", "content": tool_results})

    print(f"  ⚠️  Max {max_iterations} tool iterations cross — loop break.")
    fallback = "Sorry bhai, mujhe is question mein confusion ho gayi. Phir se try karo."
    messages.append({"role": "assistant", "content": fallback})
    return fallback


# ============================================================
# MAIN LOOP
# ============================================================

print(f"Guru chalu (provider: {PROVIDER} | model: {MODEL}) 🧠⚡")
print("'exit' likho band karne ke liye, 'reset' memory clear karne ke liye.\n")

while True:
    user_input = input("Aap: ")

    if user_input.lower() == "exit":
        print("Bye bhai!")
        break

    if user_input.lower() == "reset":
        messages = fresh_messages()
        print("Guru: Memory reset!\n")
        continue

    try:
        reply = run_agent_turn(user_input)
        print(f"Guru: {reply}\n")
    except Exception as e:
        err_str = str(e)
        # Groq-specific: model ne galti se tool call kar diya
        if "tool_use_failed" in err_str or "Failed to call a function" in err_str:
            print("  ⚠️  Model ne tool call mein galti ki — clean retry karta hoon...")
            if messages and messages[-1].get("role") == "user":
                messages.pop()
            try:
                reply = run_agent_turn(user_input)
                print(f"Guru: {reply}\n")
            except Exception as e2:
                print(f"Guru: Retry bhi fail — {type(e2).__name__}\n")
        else:
            print(f"Guru: Error aaya — {type(e).__name__}: {e}\n")
