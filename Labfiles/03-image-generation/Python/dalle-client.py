import os
import json

# Add references
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai import AzureOpenAI
import requests

def main(): 

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')
        
    try: 
    
        # Get configuration settings 
        load_dotenv()
        project_connection = os.getenv("PROJECT_CONNECTION")
        model_deployment =  os.getenv("MODEL_DEPLOYMENT")
        
        # Initialize the project client
        project_client = AIProjectClient.from_connection_string(
            conn_str=project_connection,
            credential=DefaultAzureCredential())
        
        ## Get an OpenAI client
        openai_client = project_client.inference.get_azure_openai_client(api_version="2024-06-01")
         
        img_no = 0
        # Loop until the user types 'quit'
        while True:
            # Get input text
            input_text = input("Enter the prompt (or type 'quit' to exit): ")
            if input_text.lower() == "quit":
                break
            if len(input_text) == 0:
                print("Please enter a prompt.")
                continue
            
            # Generate an image
            result = openai_client.images.generate(
                model=model_deployment,
                prompt=input_text,
                n=1
            )

            json_response = json.loads(result.model_dump_json())
            image_url = json_response["data"][0]["url"]

            # save the image
            img_no += 1
            file_name = f"image_{img_no}.png"
            save_image (image_url, file_name)


    except Exception as ex:
        print(ex)

def save_image (image_url, file_name):
    # Set the directory for the stored image
    image_dir = os.path.join(os.getcwd(), 'images')

    # If the directory doesn't exist, create it
    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)

    # Initialize the image path (note the filetype should be png)
    image_path = os.path.join(image_dir, file_name)

    # Retrieve the generated image
    generated_image = requests.get(image_url).content  # download the image
    with open(image_path, "wb") as image_file:
        image_file.write(generated_image)
    print (f"Image saved as {image_path}")


if __name__ == '__main__': 
    main()