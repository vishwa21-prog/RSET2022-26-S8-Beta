import whisper

model = whisper.load_model("base")
result = model.transcribe(r"C:\Users\elwin\Downloads\Standard recording 560.mp3")  # Replace with your actual file
print(result["text"])
