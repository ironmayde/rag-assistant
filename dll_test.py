def test_import(name):
    print(f"\nTesting import: {name}")

    try:
        module = __import__(name)
        print(f"SUCCESS: {name} imported.")
    except Exception as error:
        print(f"FAILED: {name}")
        print("Error:")
        print(error)


def main():
    print("DLL dependency test started.")

    test_import("foundry_local_sdk")
    test_import("foundry_local_core")
    test_import("foundry_local_core_winml")
    test_import("onnxruntime")
    test_import("onnxruntime_genai")


if __name__ == "__main__":
    main()