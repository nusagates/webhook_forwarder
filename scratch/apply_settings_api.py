import os

main_path = "d:/Project/Python/webhook_forwarder/main.py"
api_path = "d:/Project/Python/webhook_forwarder/scratch/append_settings_api.py"

with open(main_path, "r", encoding="utf-8") as f:
    main_content = f.read()

with open(api_path, "r", encoding="utf-8") as f:
    api_content = f.read()

# Append it before the `if __name__ == "__main__":` block if it exists, or at the end
if "if __name__ == \"__main__\":" in main_content:
    main_content = main_content.replace(
        "if __name__ == \"__main__\":",
        api_content + "\nif __name__ == \"__main__\":"
    )
else:
    main_content += "\n" + api_content

with open(main_path, "w", encoding="utf-8") as f:
    f.write(main_content)
    
print("Appended APIs to main.py")
