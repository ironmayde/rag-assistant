import asyncio

from foundry_local_sdk import Configuration, FoundryLocalManager


async def main():
    print("Foundry Local chat test started.")

    config = Configuration(app_name="rag-assistant")
    FoundryLocalManager.initialize(config)

    manager = FoundryLocalManager.instance
    print("FoundryLocalManager initialized successfully.")

    model = manager.catalog.get_model("qwen2.5-0.5b")
    print("Model selected:", model.alias)
    print("Model ID:", model.id)

    if not model.is_cached:
        print("\nDownloading model...")
        model.download(lambda progress: print(f"\rDownloading: {progress:.0f}%", end="", flush=True))
        print("\nDownload completed.")
    else:
        print("\nModel already downloaded.")

    print("\nLoading model...")
    model.load()
    print("Model loaded successfully.")

    client = model.get_chat_client()
    print("Chat client created successfully.")

    response = client.complete_chat([
        {
            "role": "system",
            "content": "You are a helpful assistant. Answer briefly and clearly."
        },
        {
            "role": "user",
            "content": "Explain RAG in one simple sentence."
        }
    ])

    print("\nModel response:")
    print(response.choices[0].message.content)

    model.unload()
    print("\nModel unloaded.")


if __name__ == "__main__":
    asyncio.run(main())