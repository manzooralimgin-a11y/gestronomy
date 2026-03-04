import { create } from "zustand";

export interface KPI {
  metric_name: string;
  value: number;
  previous_value: number | null;
  target_value: number | null;
}

export interface AgentActivity {
  id: number;
  agent_name: string;
  action_type: string;
  description: string;
  status: string;
  created_at: string;
}

export interface AlertItem {
  id: number;
  module: string;
  severity: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface ExceptionInboxItem {
  id: number;
  source_type: string;
  module: string;
  severity: string;
  title: string;
  message: string;
  owner: string;
  status: string;
  impact_score: number;
  sla_minutes: number;
  sla_status: string;
  due_at: string | null;
  recommended_actions: string[];
  created_at: string;
}

export interface ExplainableRecommendation {
  id: number;
  agent_name: string;
  title: string;
  recommendation: string;
  rationale: string;
  confidence: number | null;
  estimated_impact: string | null;
  requires_approval: boolean;
  rollback_strategy: string | null;
  status: string;
  created_at: string;
}

export interface AuditTimelineEvent {
  id: string;
  event_type: string;
  actor_type: string;
  actor_name: string;
  entity_type: string | null;
  entity_id: number | null;
  action: string;
  detail: string;
  created_at: string;
}

interface DashboardState {
  kpis: KPI[];
  agentActivity: AgentActivity[];
  alerts: AlertItem[];
  exceptions: ExceptionInboxItem[];
  recommendations: ExplainableRecommendation[];
  auditTimeline: AuditTimelineEvent[];
  setKPIs: (kpis: KPI[]) => void;
  setAgentActivity: (activities: AgentActivity[]) => void;
  addAgentActivity: (activity: AgentActivity) => void;
  setAlerts: (alerts: AlertItem[]) => void;
  setExceptions: (items: ExceptionInboxItem[]) => void;
  setRecommendations: (items: ExplainableRecommendation[]) => void;
  setAuditTimeline: (items: AuditTimelineEvent[]) => void;
  markAlertRead: (id: number) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  kpis: [],
  agentActivity: [],
  alerts: [],
  exceptions: [],
  recommendations: [],
  auditTimeline: [],
  setKPIs: (kpis) => set({ kpis }),
  setAgentActivity: (activities) => set({ agentActivity: activities }),
  addAgentActivity: (activity) =>
    set((state) => ({
      agentActivity: [activity, ...state.agentActivity].slice(0, 50),
    })),
  setAlerts: (alerts) => set({ alerts }),
  setExceptions: (items) => set({ exceptions: items }),
  setRecommendations: (items) => set({ recommendations: items }),
  setAuditTimeline: (items) => set({ auditTimeline: items }),
  markAlertRead: (id) =>
    set((state) => ({
      alerts: state.alerts.map((a) =>
        a.id === id ? { ...a, is_read: true } : a
      ),
    })),
}));
