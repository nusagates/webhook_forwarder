import os
import re

# Update SystemLimits.tsx
sl_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/SystemLimits.tsx"
with open(sl_path, "r", encoding="utf-8") as f:
    sl_content = f.read()

# Add to state
old_state = """    const [limits, setLimits] = useState({
        max_projects_per_user: 5,
        max_endpoints_per_project: 10,
        max_logs_per_endpoint: 1000
    });"""

new_state = """    const [limits, setLimits] = useState({
        max_projects_per_user: 5,
        max_endpoints_per_project: 10,
        max_logs_per_endpoint: 1000,
        max_destinations_per_endpoint: 5
    });"""
sl_content = sl_content.replace(old_state, new_state)

# Add to UI
old_ui = """                    </Box>
                </Box>

                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>"""

new_ui = """                    </Box>
                    <Divider sx={{ my: 3 }} />
                    <Box>
                        <Typography variant="h6" gutterBottom>Max Destinations per Endpoint</Typography>
                        <Typography variant="body2" color="text.secondary" paragraph>
                            The maximum number of forwarding destinations a user can add to a single endpoint.
                        </Typography>
                        <TextField
                            fullWidth
                            type="number"
                            name="max_destinations_per_endpoint"
                            value={limits.max_destinations_per_endpoint}
                            onChange={handleChange}
                        />
                    </Box>
                </Box>

                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>"""
sl_content = sl_content.replace(old_ui, new_ui)

with open(sl_path, "w", encoding="utf-8") as f:
    f.write(sl_content)


# Update UserManagement.tsx
um_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/UserManagement.tsx"
with open(um_path, "r", encoding="utf-8") as f:
    um_content = f.read()

# Add to LimitData
if "limit_destinations" not in um_content:
    um_content = um_content.replace("limit_logs: number | null;", "limit_logs: number | null;\n    limit_destinations: number | null;")
    um_content = um_content.replace("limit_logs: null", "limit_logs: null,\n        limit_destinations: null")

    old_edit_ui = """                            value={editData.limit_logs === null ? '' : editData.limit_logs}
                            onChange={(e) => setEditData({...editData, limit_logs: e.target.value === '' ? null : parseInt(e.target.value)})}
                            helperText="Leave empty to use system default"
                        />
                    </Box>
                </DialogContent>"""

    new_edit_ui = """                            value={editData.limit_logs === null ? '' : editData.limit_logs}
                            onChange={(e) => setEditData({...editData, limit_logs: e.target.value === '' ? null : parseInt(e.target.value)})}
                            helperText="Leave empty to use system default"
                        />
                        <TextField
                            margin="dense"
                            label="Max Destinations/Endpoint (Custom Limit)"
                            type="number"
                            fullWidth
                            value={editData.limit_destinations === null ? '' : editData.limit_destinations}
                            onChange={(e) => setEditData({...editData, limit_destinations: e.target.value === '' ? null : parseInt(e.target.value)})}
                            helperText="Leave empty to use system default"
                        />
                    </Box>
                </DialogContent>"""
    um_content = um_content.replace(old_edit_ui, new_edit_ui)
    
    with open(um_path, "w", encoding="utf-8") as f:
        f.write(um_content)

print("Updated SystemLimits.tsx and UserManagement.tsx")
