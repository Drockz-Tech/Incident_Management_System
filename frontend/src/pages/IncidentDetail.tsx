import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, ServerCrash, ShieldAlert } from 'lucide-react';
import RCAForm from '../components/RCAForm';

export default function IncidentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [incident, setIncident] = useState<any>(null);
  const [signals, setSignals] = useState<any[]>([]);

  useEffect(() => {
    const fetchDetails = async () => {
      const incRes = await fetch(`/api/incidents`);
      const all = await incRes.json();
      const current = all.find((i: any) => i.id === id);
      if (current) {
        setIncident(current);
        const sigRes = await fetch(`/api/incidents/${id}/signals`);
        if (sigRes.ok) {
          setSignals(await sigRes.json());
        }
      }
    };
    fetchDetails();
  }, [id]);

  const handleStateChange = async (newState: string, rcaData?: any) => {
    try {
      const res = await fetch(`/api/incidents/${id}/transition`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: newState, rca: rcaData })
      });
      if (res.ok) {
        const updated = await res.json();
        setIncident(updated);
      } else {
        const error = await res.json();
        alert(error.detail || "Failed to update state");
      }
    } catch (e) {
      console.error(e);
      alert("An error occurred");
    }
  };

  if (!incident) return <div className="text-center py-20 animate-pulse text-primary">Loading Incident Data...</div>;

  return (
    <div className="space-y-6">
      <button onClick={() => navigate('/')} className="flex items-center text-slate-400 hover:text-white transition-colors">
        <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboard
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel">
            <h2 className="text-2xl font-bold flex items-center mb-4">
              <ServerCrash className="w-6 h-6 mr-3 text-slate-400" />
              {incident.component_id}
            </h2>
            <div className="flex space-x-4 mb-6">
              <span className="px-3 py-1 rounded bg-slate-800 text-sm">Status: <strong>{incident.state}</strong></span>
              <span className="px-3 py-1 rounded bg-slate-800 text-sm">Severity: <strong>{incident.alert_level}</strong></span>
            </div>
            
            <h3 className="text-lg font-semibold mb-3 border-b border-slate-700 pb-2">Recent Signals (Raw)</h3>
            <div className="bg-slate-900 rounded-lg p-4 h-96 overflow-y-auto space-y-3 font-mono text-sm">
              {signals.map((sig, i) => (
                <div key={i} className="border-l-2 border-danger pl-3 py-1">
                  <div className="text-slate-400 text-xs">{new Date(sig.timestamp).toLocaleString()}</div>
                  <div className="text-danger font-bold">{sig.error_type}</div>
                  <div className="text-slate-300">{sig.message}</div>
                </div>
              ))}
              {signals.length === 0 && <div className="text-slate-500">No signals found.</div>}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="glass-panel">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <ShieldAlert className="w-5 h-5 mr-2 text-warning" />
              Workflow Actions
            </h3>
            <div className="space-y-3">
              {incident.state === 'OPEN' && (
                <button onClick={() => handleStateChange('INVESTIGATING')} className="w-full btn-primary bg-warning hover:bg-yellow-600">
                  Acknowledge & Investigate
                </button>
              )}
              {incident.state === 'INVESTIGATING' && (
                <button onClick={() => handleStateChange('RESOLVED')} className="w-full btn-primary bg-success hover:bg-emerald-600">
                  Mark as Resolved
                </button>
              )}
              {incident.state === 'RESOLVED' && (
                <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                  <p className="text-sm text-slate-400 mb-4">A Root Cause Analysis is required to close this incident.</p>
                  <RCAForm onSubmit={(data) => handleStateChange('CLOSED', data)} />
                </div>
              )}
              {incident.state === 'CLOSED' && (
                <div className="text-success font-semibold flex items-center justify-center p-4 bg-success/10 rounded border border-success/20">
                  Incident Successfully Closed
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
