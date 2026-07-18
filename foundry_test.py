import asyncio


async def main():
    print("Foundry Local catalog test started.")

    try:
        from foundry_local_sdk import Configuration, FoundryLocalManager

        config = Configuration(app_name="rag-assistant")
        FoundryLocalManager.initialize(config)

        manager = FoundryLocalManager.instance
        print("FoundryLocalManager initialized successfully.")

        models = manager.catalog.list_models()
        print(f"Models available: {len(models)}")

        print("\nFirst available models:")
        for model in models[:5]:
            print(model)

    except Exception as error:
        print("Foundry Local catalog test failed.")
        print("Error:")
        print(error)


if __name__ == "__main__":
    asyncio.run(main())