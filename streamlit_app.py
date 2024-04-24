import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="Snowflake Arctic")

# Replicate Credentials
with st.sidebar:
    st.title("Snowflake Arctic")
    if "REPLICATE_API_TOKEN" in st.secrets:
        replicate_api = st.secrets["REPLICATE_API_TOKEN"]
    else:
        replicate_api = st.text_input("Enter Replicate API token:", type="password")
        if not (replicate_api.startswith("r8_") and len(replicate_api) == 40):
            st.warning(
                "Please enter your Replicate API token, or head over to [Replicate](https://replicate.com) to create one.",
                icon="⚠️",
            )

    os.environ["REPLICATE_API_TOKEN"] = replicate_api
    st.subheader("Adjust model parameters")
    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.01,
        max_value=5.0,
        value=0.6,
        step=0.01,
        help="Controls the randomness of the generated text. A lower value makes the output more deterministic, while a higher value introduces more randomness.",
    )
    top_p = st.sidebar.slider(
        "Top p",
        min_value=0.01,
        max_value=1.0,
        value=0.9,
        step=0.01,
        help="Controls the variety of responses. Lower values focus on fewer options, while higher values explore more diverse options.",
    )

# Store LLM-generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi. I'm Arctic, a new, efficient, intelligent, and truly open language model created by Snowflake AI Research. Ask me anything.",
        }
    ]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


def clear_chat_history():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi. I'm Arctic, a new, efficient, intelligent, and truly open language model created by Snowflake AI Research. Ask me anything.",
        }
    ]


st.sidebar.button("Clear chat history", on_click=clear_chat_history)

st.sidebar.caption(
    "Built by [Snowflake](https://snowflake.com/) to demonstrate [Snowflake Arctic](https://www.snowflake.com/blog/arctic-open-and-efficient-foundation-language-models-snowflake). App hosted on [Streamlit Community Cloud](https://streamlit.io/cloud). Model hosted by [Replicate](https://replicate.com/snowflake/snowflake-arctic-instruct)."
)


# Function for generating Snowflake Arctic response
def generate_arctic_response():
    prompt = []
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
        else:
            prompt.append(
                "<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>"
            )

    prompt.append("<|im_start|>assistant")
    prompt.append("")

    for event in replicate.stream(
        "snowflake/snowflake-arctic-instruct",
        input={
            "prompt": "\n".join(prompt),
            "prompt_template": r"{prompt}",
            "temperature": temperature,
            "top_p": top_p,
        },
    ):
        yield str(event)


# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response = generate_arctic_response()
        full_response = st.write_stream(response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
