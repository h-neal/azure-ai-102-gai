import os
import openai
import dotenv
import time

dotenv.load_dotenv()

endpoint = os.environ.get("AZURE_OAI_ENDPOINT")
api_key = os.environ.get("AZURE_OAI_KEY")
deployment = os.environ.get("AZURE_OAI_DEPLOYMENT")

client = openai.AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-02-01",
)

text = input('\nEnter a question:\n')

completion = None  # Ensure it's always defined

for attempt in range(3):
    try:
        completion = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "user",
                    "content": text,
                },
            ],
            extra_body={
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": os.environ["AZURE_SEARCH_ENDPOINT"],
                            "index_name": os.environ["AZURE_SEARCH_INDEX"],
                            "authentication": {
                                "type": "api_key",
                                "key": os.environ["AZURE_SEARCH_KEY"],
                            }
                        }
                    }
                ],
            }
        )
        break  # Success
    except openai.BadRequestError as e:
        # Check if it's a 429 inside a BadRequest
        if "429" in str(e):
            print("⚠️ Rate limit hit. Retrying in 60 seconds...")
            time.sleep(60)
        else:
            print(f"❌ Bad request: {e}")
            break
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        break

if completion:
    print(completion.model_dump_json(indent=2))
else:
    print("❌ Request failed.")
