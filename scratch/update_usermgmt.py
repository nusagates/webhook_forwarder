import os
import re

file_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/UserManagement.tsx"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add block dialog state
if "const [blockOpen, setBlockOpen]" not in content:
    content = content.replace("const [editOpen, setEditOpen] = useState(false);", 
        "const [editOpen, setEditOpen] = useState(false);\n    const [blockOpen, setBlockOpen] = useState(false);\n    const [blockReason, setBlockReason] = useState('');\n    const [userToBlock, setUserToBlock] = useState<any>(null);")

# Update toggleBlock logic
old_toggle = """    const toggleBlock = async (user: any) => {
        if (!await confirm({ message: `Are you sure you want to ${user.is_blocked ? 'unblock' : 'block'} ${user.email}?`, isDanger: true })) return;
        try {
            await fetchApi(`/api/admin/users/${user.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    is_admin: user.is_admin,
                    is_blocked: !user.is_blocked,
                    limit_projects: user.limit_projects,
                    limit_endpoints: user.limit_endpoints,
                    limit_logs: user.limit_logs
                })
            });
            toast.success(user.is_blocked ? 'User unblocked' : 'User blocked');
            fetchUsers();
        } catch (e: any) {
            toast.error(e.message || "Failed to update block status");
        }
    };"""

new_toggle = """    const toggleBlock = async (user: any) => {
        if (!user.is_blocked) {
            setUserToBlock(user);
            setBlockReason('');
            setBlockOpen(true);
            return;
        }
        
        if (!await confirm({ message: `Are you sure you want to unblock ${user.email}?`, isDanger: true })) return;
        executeBlockToggle(user, false, "");
    };

    const executeBlockToggle = async (user: any, block: boolean, reason: string) => {
        try {
            await fetchApi(`/api/admin/users/${user.id}`, {
                method: 'PUT',
                body: JSON.stringify({
                    is_admin: user.is_admin,
                    is_blocked: block,
                    block_reason: block ? reason : null,
                    limit_projects: user.limit_projects,
                    limit_endpoints: user.limit_endpoints,
                    limit_logs: user.limit_logs
                })
            });
            toast.success(block ? 'User blocked' : 'User unblocked');
            fetchUsers();
        } catch (e: any) {
            toast.error(e.message || "Failed to update block status");
        }
    };
    
    const submitBlock = () => {
        if (!userToBlock) return;
        executeBlockToggle(userToBlock, true, blockReason);
        setBlockOpen(false);
    };"""

content = content.replace(old_toggle, new_toggle)

# Add Dialog JSX at the end of the return statement
old_jsx_end = """            </Dialog>
        </Box>
    );
}"""

new_jsx_end = """            </Dialog>

            {/* Block Dialog */}
            <Dialog open={blockOpen} onClose={() => setBlockOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Block User</DialogTitle>
                <DialogContent>
                    <Typography paragraph>
                        Please provide a reason for blocking <strong>{userToBlock?.email}</strong>. This reason will be shown to the user when they try to access the application.
                    </Typography>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Reason for suspension"
                        type="text"
                        fullWidth
                        variant="outlined"
                        value={blockReason}
                        onChange={(e) => setBlockReason(e.target.value)}
                        placeholder="e.g. Violation of terms of service"
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setBlockOpen(false)}>Cancel</Button>
                    <Button onClick={submitBlock} color="error" variant="contained">Block User</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}"""

content = content.replace(old_jsx_end, new_jsx_end)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated UserManagement.tsx successfully")
