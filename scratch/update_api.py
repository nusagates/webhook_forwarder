import os

api_path = "d:/Project/Python/webhook_forwarder/frontend/src/api.ts"
with open(api_path, "r", encoding="utf-8") as f:
    content = f.read()

old_error_handling = """    if !response.ok:
        const errorData = await response.json().catch(() => ({}));"""

new_error_handling = """    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        
        // Handle blocked user redirect
        if (response.status === 403 && errorData.detail && errorData.detail.code === 'ACCOUNT_BLOCKED') {
            localStorage.setItem('block_reason', errorData.detail.reason || 'No reason provided.');
            if (window.location.pathname !== '/blocked') {
                window.location.href = '/blocked';
            }
            throw new Error('Account blocked');
        }"""

# Actually, the original line was `if (!response.ok) {`
if "ACCOUNT_BLOCKED" not in content:
    content = content.replace("    if (!response.ok) {\n        const errorData = await response.json().catch(() => ({}));", new_error_handling)
    with open(api_path, "w", encoding="utf-8") as f:
        f.write(content)
print("Updated api.ts successfully")
