import streamlit as st
from PIL import Image
import soundfile as sf
import torch
from transformers import AutoProcessor, AutoModelForMultimodalLM, BitsAndBytesConfig
import time

st.set_page_config(page_title="🟢 Offline Gemini Live", layout="wide")

# ====================== MODEL LOADING ======================
@st.cache_resource
def load_model():
    MODEL_ID = "google/gemma-4-E2B-it"
    st.info("Loading Gemma 4 E2B-it in 8-bit mode... (this may take a moment)")
    
    quant_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_skip_modules=["vision_tower"]
    )

    processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
    model = AutoModelForMultimodalLM.from_pretrained(
        MODEL_ID,
        # quantization_config=quant_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16
    )
    st.success("✅ Gemma 4 E42-it loaded successfully!")
    return processor, model

processor, model = load_model()

# ====================== GEMMA_RUN ======================
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

# ====================== UI ======================
st.title("🟢 Offline Gemini Live")
st.caption("Gemma 4 E4B-it • Fully Offline • One photo per click")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "image" in msg and msg["image"] is not None:
            st.image(msg["image"])

# Camera + Input
col1, col2 = st.columns([3, 2])

with col1:
    camera_input = st.camera_input("📹 Live Camera Preview", key="camera")

with col2:
    st.markdown("### Controls")
    capture_btn = st.button("📸 Capture Current Frame", type="primary", use_container_width=True)
    audio_input = st.audio_input("🎤 Voice Message")

# Capture logic
if capture_btn and camera_input is not None:
    # Store the captured image
    st.session_state.captured_image = camera_input
    st.success("✅ Photo captured! Review it below and click 'Send to Gemma 4'")

# Show captured image for review
if "captured_image" in st.session_state:
    st.image(st.session_state.captured_image, caption="Captured Image")

# Text input
text_input = st.chat_input("Type your message (optional)")

# Send button
if st.button("🚀 Send to Gemma 4", type="primary", use_container_width=True):
    user_text = text_input or "Describe this image in detail."

    # Add user message
    with st.chat_message("user"):
        st.markdown(user_text)
        if "captured_image" in st.session_state:
            st.image(st.session_state.captured_image)

    # Prepare input
    content = [{"type": "text", "text": user_text}]
    if "captured_image" in st.session_state:
        content.append({"type": "image", "image": Image.open(st.session_state.captured_image)})
    if audio_input is not None:
        waveform, sample_rate = sf.read(audio_input)
        content.append({"type": "audio", "audio": waveform})

    messages = [{"role": "user", "content": content}]

    # Run Gemma 4
    with st.spinner("Gemma 4 is thinking..."):
        response, latency = gemma_run(messages, enable_thinking=True)

    # Display response
    with st.chat_message("assistant"):
        st.markdown(response)
        st.caption(f"⏱️ Processed in {latency} seconds")

    # Save to history
    st.session_state.messages.append({"role": "user", "content": user_text, "image": st.session_state.get("captured_image")})
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Clear captured image after sending
    if "captured_image" in st.session_state:
        del st.session_state.captured_image

    st.rerun()