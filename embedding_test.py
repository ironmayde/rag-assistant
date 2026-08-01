from foundry_local_sdk import Configuration, FoundryLocalManager
from foundry_local_sdk.exception import FoundryLocalException


def main():
    config = Configuration(app_name="rag-assistant-embedding-test")

    try:
        FoundryLocalManager.initialize(config)
    except FoundryLocalException as error:
        if "singleton" not in str(error).lower():
            raise error

    manager = FoundryLocalManager.instance

    print("Embedding model is being prepared...")

    model = manager.catalog.get_model("qwen3-embedding-0.6b")

    if not model.is_cached:
        print("Embedding model is being downloaded...")
        model.download()

    model.load()
    print("Embedding model loaded successfully.")

    client = model.get_embedding_client()

    response = client.generate_embedding(
        "Retrieval-Augmented Generation uses retrieved information."
    )

    embedding = response.data[0].embedding

    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")

    model.unload()
    print("Embedding model test completed successfully.")


if __name__ == "__main__":
    main()