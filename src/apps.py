import streamlit as st
from PIL import Image
import soundfile as sf
import torch
from transformers import AutoProcessor, AutoModelForMultimodalLM, BitsAndBytesConfig
import time

st.set_page_config(page_title="🟢 Offline Gemini Live", layout="wide")

# ====================== MODEL LOADING (Cached) ======================
@st.cache_resource
def load_model():
    MODEL_ID = "google/gemma-4-E2B-it"
    st.info(f"Loading Gemma 4 {MODEL_ID} in 8-bit mode... (this may take 1-2 minutes)")

    quant_config = BitsAndBytesConfig(
        load_in_8bit=True,
        # llm_int8_skip_modules=["vision_tower"]
    )

    processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
    model = AutoModelForMultimodalLM.from_pretrained(
        MODEL_ID,
        # quantization_config=quant_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16
    )
    st.success("✅ Gemma 4 E4B-it loaded successfully!")
    return processor, model

processor, model = load_model()

# ====================== GEMMA_RUN FUNCTION ======================
def gemma_run(messages, max_new_tokens=1024, temperature=0.7, enable_thinking=False):
    start = time.time()
    
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt"
    ).to(model.device)
    
    input_len = inputs["input_ids"].shape[-1]
    
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=True,
        top_p=0.95
    )
    
    response = processor.decode(outputs[0][input_len:], skip_special_tokens=True)
    latency = round(time.time() - start, 2)
    return response, latency

# ====================== STREAMLIT UI ======================
st.title("🟢 Offline Gemini Live")
st.caption("Powered by Gemma 4 E2B-it • Fully Offline • Text + Camera + Voice")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image" in msg and msg["image"] is not None:
            st.image(msg["image"])

# Input area
text_input = st.chat_input("Type your message...")

col1, col2 = st.columns([1, 1])
with col1:
    camera_input = st.camera_input("📸 Take a photo") # continous capture version
with col2:
    audio_input = st.audio_input("🎤 Record voice message")

# Process user input
if text_input or camera_input is not None or audio_input is not None:
    user_text = text_input or ("Voice message" if audio_input is not None else "Photo message")

    # Add user message
    with st.chat_message("user"):
        st.markdown(user_text)
        if camera_input is not None:
            st.image(camera_input)
        if audio_input is not None:
            st.audio(audio_input)

    # Prepare multimodal content
    content = [{"type": "text", "text": user_text}]
    
    if camera_input is not None:
        content.append({"type": "image", "image": Image.open(camera_input)})
    if audio_input is not None:
        waveform, sample_rate = sf.read(audio_input)
        content.append({"type": "audio", "audio": waveform})

    messages = [{"role": "user", "content": content}]

    # Call Gemma 4
    with st.spinner("Gemma 4 is thinking..."):
        response, latency = gemma_run(messages, enable_thinking=True)

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
        st.caption(f"⏱️ Processed in {latency} seconds")

    # Save to history
    st.session_state.messages.append({"role": "user", "content": user_text, "image": camera_input})
    st.session_state.messages.append({"role": "assistant", "content": response})

    st.rerun()