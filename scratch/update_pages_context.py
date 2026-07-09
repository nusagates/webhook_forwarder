import os
import re

# Update Endpoints.tsx
endpoints_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/Endpoints.tsx"
with open(endpoints_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace local project states with context
if "import { useProject } from '../contexts/ProjectContext';" not in content:
    content = content.replace("import { fetchApi } from '../api';", "import { fetchApi } from '../api';\nimport { useProject } from '../contexts/ProjectContext';")

old_states = """    const [projects, setProjects] = useState<Project[]>([]);
    const [selectedProjectId, setSelectedProjectId] = useState<string>('');"""
new_states = """    const { projects, selectedProjectId } = useProject();"""
content = content.replace(old_states, new_states)

# Remove loadProjects
old_load = """    useEffect(() => {
        document.title = "Endpoints - Webhook Forwarder";
        loadProjects();
    }, []);
    useEffect(() => {
        if (selectedProjectId) loadEndpoints(selectedProjectId);
        else setEndpoints([]);
    }, [selectedProjectId]);

    const loadProjects = async () => {
        try { setProjects(await fetchApi('/api/projects')); }
        catch (err) { console.error(err); }
    };"""

new_load = """    useEffect(() => {
        document.title = "Endpoints - Webhook Forwarder";
    }, []);
    
    useEffect(() => {
        if (selectedProjectId) loadEndpoints(selectedProjectId);
        else setEndpoints([]);
    }, [selectedProjectId]);"""
content = content.replace(old_load, new_load)

# Remove UI for selecting projects in Endpoints
project_select_ui = """                <Box sx={{ minWidth: 250 }}>
                    <FormControl fullWidth size="small">
                        <InputLabel>Select Project</InputLabel>
                        <Select
                            value={selectedProjectId}
                            label="Select Project"
                            onChange={(e) => setSelectedProjectId(e.target.value as string)}
                        >
                            <MenuItem value=""><em>None</em></MenuItem>
                            {projects.map((p) => (
                                <MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Box>"""
content = content.replace(project_select_ui, "")

with open(endpoints_path, "w", encoding="utf-8") as f:
    f.write(content)

# Update LiveLogs.tsx
livelogs_path = "d:/Project/Python/webhook_forwarder/frontend/src/pages/LiveLogs.tsx"
with open(livelogs_path, "r", encoding="utf-8") as f:
    content = f.read()

if "import { useProject } from '../contexts/ProjectContext';" not in content:
    content = content.replace("import { fetchApi } from '../api';", "import { fetchApi } from '../api';\nimport { useProject } from '../contexts/ProjectContext';")

old_log_states = """    const [projects, setProjects] = useState<Project[]>([]);
    const [selectedProjectId, setSelectedProjectId] = useState<string>('');"""
new_log_states = """    const { projects, selectedProjectId } = useProject();"""
content = content.replace(old_log_states, new_log_states)

old_log_load = """    useEffect(() => {
        loadProjects();
    }, []);

    useEffect(() => {
        if (selectedProjectId) {
            loadEndpoints(selectedProjectId);
        } else {
            setEndpoints([]);
            setSelectedEndpointId('');
        }
    }, [selectedProjectId]);

    const loadProjects = async () => {
        try {
            const data = await fetchApi('/api/projects');
            setProjects(data);
        } catch (err) {
            console.error('Failed to load projects', err);
        }
    };"""

new_log_load = """    useEffect(() => {
        if (selectedProjectId) {
            loadEndpoints(selectedProjectId);
        } else {
            setEndpoints([]);
            setSelectedEndpointId('');
        }
    }, [selectedProjectId]);"""
content = content.replace(old_log_load, new_log_load)

log_project_ui = """                    <FormControl sx={{ minWidth: 200 }} size="small">
                        <InputLabel>Project</InputLabel>
                        <Select
                            value={selectedProjectId}
                            label="Project"
                            onChange={(e) => setSelectedProjectId(e.target.value as string)}
                        >
                            <MenuItem value=""><em>None</em></MenuItem>
                            {projects.map((p) => (
                                <MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>"""
content = content.replace(log_project_ui, "")

with open(livelogs_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated Endpoints and LiveLogs successfully")
