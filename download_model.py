from TTS.api import TTS
import torch

# This is the model name your voice_engine.py is configured to use.
model_name = "tts_models/en/vctk/vits"

print(f"--- Attempting to download and cache the TTS model: {model_name} ---")

try:
    # Check if a GPU is available, otherwise use CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Initializing the TTS object with a model name will trigger
    # the download if the model is not found locally.
    tts = TTS(model_name=model_name, progress_bar=True).to(device)
    
    print("\n--- Model downloaded and loaded successfully! ---")
    print("The model is now cached and ready for the main application to use.")

except Exception as e:
    print(f"\n--- An error occurred: {e} ---")
    print("Please check the error message. It might be a network issue or a problem with the TTS library installation.")
