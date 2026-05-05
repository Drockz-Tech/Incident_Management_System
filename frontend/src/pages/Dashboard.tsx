import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, Clock, ServerCrash, ActivitySquare } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface WorkItem {
  id: string;
  component_id: string;
  state: string;
  alert_level: string;
  created_at: string;
  updated_at: string;
}

export default function Dashboard() {
  const [incidents, setIncidents] = useState<WorkItem[]>([]);

  useEffect(() => {
    const fetchIncidents = async () => {
      const res = await fetch('/api/incidents');
      if (res.ok) {
        setIncidents(await res.json());
      }
    };
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 5000); // Polling every 5s for demo
    return () => clearInterval(interval);
  }, []);

  const getAlertColor = (level: string) => {
    switch (level) {
      case 'P0': return 'text-danger bg-danger/10 border-danger/20';
      case 'P1': return 'text-warning bg-warning/10 border-warning/20';
      case 'P2': return 'text-primary bg-primary/10 border-primary/20';
      default: return 'text-slate-400 bg-slate-800 border-slate-700';
    }
  };

  const getStateBadge = (state: string) => {
    const colors: Record<string, string> = {
      OPEN: 'bg-danger/20 text-danger',
      INVESTIGATING: 'bg-warning/20 text-warning',
      RESOLVED: 'bg-primary/20 text-primary',
      CLOSED: 'bg-success/20 text-success'
    };
    return <span className={`text-xs font-semibold px-2 py-1 rounded-full ${colors[state] || 'bg-slate-700'}`}>{state}</span>;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Active Incidents</h2>
        <div className="flex items-center space-x-2 text-sm text-slate-400">
          <ActivitySquare className="w-4 h-4 animate-pulse text-success" />
          <span>System Monitoring Active</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {incidents.map((incident) => (
          <Link to={`/incident/${incident.id}`} key={incident.id} className="block group">
            <div className="glass-panel h-full flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-4">
                  <div className={`px-3 py-1 rounded-full border text-xs font-bold ${getAlertColor(incident.alert_level)} flex items-center`}>
                    <AlertCircle className="w-3 h-3 mr-1" />
                    {incident.alert_level}
                  </div>
                  {getStateBadge(incident.state)}
                </div>
                <h3 className="text-xl font-semibold mb-2 group-hover:text-primary transition-colors flex items-center">
                  <ServerCrash className="w-5 h-5 mr-2 text-slate-400" />
                  {incident.component_id}
                </h3>
              </div>
              <div className="flex items-center text-sm text-slate-500 mt-4 pt-4 border-t border-slate-700/50">
                <Clock className="w-4 h-4 mr-1" />
                Started {formatDistanceToNow(new Date(incident.created_at))} ago
              </div>
            </div>
          </Link>
        ))}
        {incidents.length === 0 && (
          <div className="col-span-full py-20 text-center text-slate-500">
            <ActivitySquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-lg">No active incidents. Systems are operating nominally.</p>
          </div>
        )}
      </div>
    </div>
  );
}
