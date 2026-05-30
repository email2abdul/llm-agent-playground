import io
import contextlib

import streamlit as st

import agent

st.set_page_config(page_title="Guru — LLM Agent")

# processing flag — streaming ke time True, baki False
# Iss flag se chat_input + sidebar controls disabled rehte hain
processing = st.session_state.get("processing", False)

# ============================================================
# SIDEBAR — provider switch + reset (processing ke time disabled)
# ============================================================
with st.sidebar:
    st.header("Settings")

    provider_options = ["anthropic", "groq"]
    selected = st.selectbox(
        "Provider",
        provider_options,
        index=provider_options.index(agent.PROVIDER),
        disabled=processing,
    )

    if selected != agent.PROVIDER:
        agent.set_provider(selected)
        agent.reset_messages()
        st.session_state.messages = []
        st.rerun()

    st.caption(f"**Model:** `{agent.MODEL}`")

    st.divider()

    if st.button("Reset conversation", use_container_width=True, disabled=processing):
        agent.reset_messages()
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("**Tools available:**")
    st.caption("- get_current_time\n- calculate\n- search_docs (RAG)")


# ============================================================
# MAIN CHAT
# ============================================================
st.title("Guru")
st.caption(f"Running on **{agent.PROVIDER}** ({agent.MODEL})")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("tools"):
            with st.expander("Tool calls", expanded=False):
                st.code(msg["tools"], language="text")
        st.markdown(msg["content"])


# ============================================================
# INPUT — processing ke time disabled
# ============================================================
user_input = st.chat_input(
    "Guru soch raha hai..." if processing else "Apna sawal yahan likho...",
    disabled=processing,
)

# Double-rerun pattern:
# Run 1: user input lo, processing flag set karo, rerun (taki input disabled dikhe)
# Run 2: pending input process karo, response stream karo, flag clear, rerun (input wapas enabled)
if user_input and not processing:
    st.session_state.processing = True
    st.session_state.pending_input = user_input
    st.rerun()

if processing and "pending_input" in st.session_state:
    pending = st.session_state.pending_input

    st.session_state.messages.append({"role": "user", "content": pending})
    with st.chat_message("user"):
        st.markdown(pending)

    with st.chat_message("assistant"):
        log_buf = io.StringIO()
        # Placeholder pehle "thinking..." dikhayega, fir streaming text se replace ho jaayega
        placeholder = st.empty()
        placeholder.markdown("_Guru soch raha hai..._")

        buffer = ""
        try:
            with contextlib.redirect_stdout(log_buf):
                for chunk in agent.run_agent_turn_stream(pending):
                    buffer += chunk
                    placeholder.markdown(buffer)
            reply = buffer if buffer else "_(no response)_"
        except Exception as e:
            reply = f"Error aaya — {type(e).__name__}: {e}"
            placeholder.error(reply)

        tool_log = log_buf.getvalue().strip()
        if tool_log:
            with st.expander("Tool calls", expanded=False):
                st.code(tool_log, language="text")

    st.session_state.messages.append(
        {"role": "assistant", "content": reply, "tools": tool_log or None}
    )

    # Processing complete — flag clear, input wapas enable
    st.session_state.processing = False
    del st.session_state.pending_input
    st.rerun()
