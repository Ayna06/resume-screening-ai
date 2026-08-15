from google import genai

# PASTE YOUR REAL API KEY HERE
client = genai.Client(api_key = "YOUR_API_KEY_HERE")

print("Available models for your key:")
for model in client.models.list():
    print(model.name)