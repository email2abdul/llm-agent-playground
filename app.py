import io
import contextlib

import streamlit as st

import agent

st.set_page_config(page_title="Guru — LLM Agent")

# ============================================================
# SIDEBAR — provider switch + reset
# ============================================================
with st.sidebar:
    st.header("Settings")

    provider_options = ["anthropic", "groq"]
    selected = st.selectbox(
        "Provider",
        provider_options,
        index=provider_options.index(agent.PROVIDER),
    )

    # Provider change ho gaya — re-init aur conversation clear karo
    # (Groq aur Anthropic ke message formats alag hain, mix nahi kar sakte)
    if selected != agent.PROVIDER:
        agent.set_provider(selected)
        agent.reset_messages()
        st.session_state.messages = []
        st.rerun()

    st.caption(f"**Model:** `{agent.MODEL}`")

    st.divider()

    if st.button("Reset conversation", use_container_width=True):
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

# Render history (with tool logs if any)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("tools"):
            with st.expander("Tool calls", expanded=False):
                st.code(msg["tools"], language="text")
        st.markdown(msg["content"])


user_input = st.chat_input("Apna sawal yahan likho...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        # Tools print karte hain stdout pe — usse capture karke UI me dikhao
        log_buf = io.StringIO()
        with st.spinner("Guru soch raha hai..."):
            try:
                with contextlib.redirect_stdout(log_buf):
                    reply = agent.run_agent_turn(user_input)
            except Exception as e:
                reply = f"Error aaya — {type(e).__name__}: {e}"

        tool_log = log_buf.getvalue().strip()
        if tool_log:
            with st.expander("Tool calls", expanded=False):
                st.code(tool_log, language="text")
        st.markdown(reply)

    st.session_state.messages.append(
        {"role": "assistant", "content": reply, "tools": tool_log or None}
    )
