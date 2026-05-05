import { useState } from 'react';

export default function RCAForm({ onSubmit }: { onSubmit: (data: any) => void }) {
  const [formData, setFormData] = useState({
    start_time: '',
    end_time: '',
    category: 'Hardware',
    fix_applied: '',
    prevention_steps: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      start_time: new Date(formData.start_time).toISOString(),
      end_time: new Date(formData.end_time).toISOString(),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-xs font-medium text-slate-400 mb-1">Start Time</label>
        <input type="datetime-local" required className="input-field text-sm" 
          value={formData.start_time} onChange={e => setFormData({...formData, start_time: e.target.value})} />
      </div>
      <div>
        <label className="block text-xs font-medium text-slate-400 mb-1">End Time</label>
        <input type="datetime-local" required className="input-field text-sm" 
          value={formData.end_time} onChange={e => setFormData({...formData, end_time: e.target.value})} />
      </div>
      <div>
        <label className="block text-xs font-medium text-slate-400 mb-1">Category</label>
        <select className="input-field text-sm" value={formData.category} onChange={e => setFormData({...formData, category: e.target.value})}>
          <option>Hardware Failure</option>
          <option>Software Bug</option>
          <option>Network Outage</option>
          <option>Human Error</option>
        </select>
      </div>
      <div>
        <label className="block text-xs font-medium text-slate-400 mb-1">Fix Applied</label>
        <textarea required className="input-field text-sm h-20" 
          value={formData.fix_applied} onChange={e => setFormData({...formData, fix_applied: e.target.value})} />
      </div>
      <div>
        <label className="block text-xs font-medium text-slate-400 mb-1">Prevention Steps</label>
        <textarea required className="input-field text-sm h-20" 
          value={formData.prevention_steps} onChange={e => setFormData({...formData, prevention_steps: e.target.value})} />
      </div>
      <button type="submit" className="w-full btn-primary mt-2">
        Submit RCA & Close
      </button>
    </form>
  );
}
