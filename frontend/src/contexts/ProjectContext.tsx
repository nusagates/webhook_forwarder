import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { fetchApi } from '../api';

interface Project {
    id: string;
    name: string;
    my_role?: string;
}

interface ProjectContextType {
    projects: Project[];
    selectedProjectId: string;
    setSelectedProjectId: (id: string) => void;
    refreshProjects: () => Promise<void>;
    loading: boolean;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export const useProject = () => {
    const context = useContext(ProjectContext);
    if (!context) {
        throw new Error('useProject must be used within a ProjectProvider');
    }
    return context;
};

export const ProjectProvider = ({ children }: { children: ReactNode }) => {
    const [projects, setProjects] = useState<Project[]>([]);
    const [selectedProjectId, setSelectedProjectId] = useState<string>(localStorage.getItem('selectedProjectId') || '');
    const [loading, setLoading] = useState(true);

    const refreshProjects = async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            setLoading(false);
            return;
        }
        try {
            const data = await fetchApi('/api/projects');
            setProjects(data);
            
            // Auto-select first project if none selected or if selected is no longer valid
            if (data.length > 0) {
                const currentStillExists = data.find((p: Project) => p.id === selectedProjectId);
                if (!selectedProjectId || !currentStillExists) {
                    setSelectedProjectId(data[0].id);
                    localStorage.setItem('selectedProjectId', data[0].id);
                }
            } else {
                setSelectedProjectId('');
                localStorage.removeItem('selectedProjectId');
            }
        } catch (err) {
            console.error("Failed to load projects", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        refreshProjects();
    }, []);

    // Save to localStorage when changed manually
    const handleSetSelectedProjectId = (id: string) => {
        setSelectedProjectId(id);
        if (id) {
            localStorage.setItem('selectedProjectId', id);
        } else {
            localStorage.removeItem('selectedProjectId');
        }
    };

    return (
        <ProjectContext.Provider 
            value={{ 
                projects, 
                selectedProjectId, 
                setSelectedProjectId: handleSetSelectedProjectId, 
                refreshProjects,
                loading
            }}
        >
            {children}
        </ProjectContext.Provider>
    );
};
