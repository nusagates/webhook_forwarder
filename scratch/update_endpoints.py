import os

# Update Endpoints.tsx
endpoints_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/Endpoints.tsx"
with open(endpoints_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add Alert and Activate Button if suspended
old_endpoint_header = """                            <Typography variant="h6">{ep.name}</Typography>
                            <Box>
                                <IconButton size="small" onClick={() => handleEditEndpoint(ep)}>
                                    <EditIcon fontSize="small" />
                                </IconButton>"""

new_endpoint_header = """                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="h6">{ep.name}</Typography>
                                {!ep.is_active && <Chip label="Suspended (Abuse)" color="error" size="small" />}
                            </Box>
                            <Box>
                                {!ep.is_active && (
                                    <Button size="small" color="success" onClick={() => handleReactivate(ep.id)} sx={{ mr: 1 }}>
                                        Reactivate
                                    </Button>
                                )}
                                <IconButton size="small" onClick={() => handleEditEndpoint(ep)}>
                                    <EditIcon fontSize="small" />
                                </IconButton>"""

if "handleReactivate" not in content:
    content = content.replace(old_endpoint_header, new_endpoint_header)
    
    # 2. Add handleReactivate function
    reactivate_func = """
    const handleReactivate = async (id: number) => {
        try {
            await fetchApi(`/api/endpoints/${id}/reactivate`, { method: 'POST' });
            toast.success('Endpoint reactivated');
            fetchEndpoints();
        } catch (e: any) {
            toast.error(e.message || "Failed to reactivate");
        }
    };
"""
    content = content.replace("const handleEditEndpoint = (ep: any) => {", reactivate_func + "\n    const handleEditEndpoint = (ep: any) => {")
    
    with open(endpoints_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Updated Endpoints.tsx successfully")
