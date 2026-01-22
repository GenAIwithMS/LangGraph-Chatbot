import uuid
import tempfile
# import streamlit as st
import streamlit as st
from app.router.database_backend import chatbot , Retrieve_all_threads
from thread_id_name import  generate_thread_id, generate_id_name
# from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
from langchain_core.messages import HumanMessage, AIMessage,ToolMessage
from app.router.database_backend import save_thread_title, get_thread_title_from_db, get_all_thread_metadata


def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id 
    add_thread(st.session_state["thread_id"])
    st.session_state["message_history"] = []
    st.session_state["thread_titles"][thread_id] = "New Chat"
    # return thread_id

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)
        if thread_id not in st.session_state["thread_titles"]:
            st.session_state["thread_titles"][thread_id] = "New Chat"


def load_conversation(thread_id):

    conversation = chatbot.get_state(config={"configurable":{"thread_id":thread_id}}).values.get("messages")
    return conversation

def get_thread_title(thread_id, user_input=None):
    # First try to fetch from DB
    db_title = get_thread_title_from_db(thread_id)
    if db_title:
        st.session_state["thread_titles"][thread_id] = db_title
        return db_title

    # Otherwise generate a new one from user_input
    if user_input:
        try:
            title = generate_id_name(user_input)
            st.session_state["thread_titles"][thread_id] = title
            save_thread_title(thread_id, title)  # ✅ persist in DB
            return title
        except Exception as e:
            print(f"Error generating title: {e}")
            return str(thread_id)[:8] + "..."
    
    return str(thread_id)[:8] + "..."


if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = Retrieve_all_threads()

if "thread_titles" not in st.session_state:
    st.session_state["thread_titles"] = get_all_thread_metadata()

add_thread(st.session_state["thread_id"])

config = {
    "configurable":{"thread_id":st.session_state["thread_id"]},
    "metadata":{"thread_id":st.session_state["thread_id"]}
    }

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

st.sidebar.title("LangGraph Chatbot")
if st.sidebar.button("New Chat"):
    reset_chat()
st.sidebar.header("My conversation")

for thread_id in st.session_state["chat_threads"][::-1]:
    title = get_thread_title(thread_id)
    if st.sidebar.button(title, key=f"thread_{thread_id}"):
        st.session_state["thread_id"] = thread_id
        messages = load_conversation(thread_id)

        tem_messages = []
        for message in messages or []:
            if isinstance(message, HumanMessage):
                role = "user_input"
            else:
                role = "assistant"

            tem_messages.append({"role": role, "content": message.content})

        st.session_state["message_history"] = tem_messages

for message in st.session_state["message_history"]:
    with st.chat_message(message['role']):
        st.text(message['content'])


user_input = st.chat_input("type here..")


if user_input and isinstance(user_input, str):  # Validate user_input
    if len(st.session_state["message_history"]) == 0:
        title = get_thread_title(st.session_state["thread_id"], user_input)


    st.session_state["message_history"].append({"role": "user_input", "content": user_input})

    with st.chat_message("user_input"):
        st.text(user_input)

    with st.chat_message("assistant"):
        # Use a mutable holder so the generator can set/modify it
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages",
            ):
                # Lazily create & update the SAME status container when any tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Finalize only if a tool was actually used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )

    # Save assistant message
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )