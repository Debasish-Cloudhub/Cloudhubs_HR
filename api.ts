import { useEffect, useState } from 'react';
import Layout from '../../components/common/Layout';
import { getHolidays, createHoliday, deleteHoliday } from '../../services/api';
import { Calendar, Plus, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import Head from 'next/head';

export default function AdminHolidaysPage() {
  const [holidays, setHolidays] = useState<any[]>([]);
  const [form, setForm] = useState({ name: '', date: '', description: '', is_optional: false });
  const [showForm, setShowForm] = useState(false);

  const fetch = async () => {
    try { const r = await getHolidays(); setHolidays(r.data); } catch {}
  };

  useEffect(() => { fetch(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createHoliday(form);
      toast.success('Holiday added');
      setForm({ name: '', date: '', description: '', is_optional: false });
      setShowForm(false);
      fetch();
    } catch { toast.error('Failed'); }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete holiday?')) return;
    try { await deleteHoliday(id); toast.success('Deleted'); fetch(); } catch { toast.error('Failed'); }
  };

  const grouped = holidays.reduce((acc: any, h: any) => {
    const month = new Date(h.date).toLocaleDateString('en-IN', { month: 'long', year: 'numeric' });
    if (!acc[month]) acc[month] = [];
    acc[month].push(h);
    return acc;
  }, {});

  return (
    <>
      <Head><title>Holidays — CloudHub HR</title></Head>
      <Layout>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="font-display font-bold text-2xl text-slate-800">Holiday Calendar</h1>
            <p className="text-slate-500 text-sm">{holidays.length} holidays</p>
          </div>
          <button onClick={() => setShowForm(!showForm)} className="btn-primary">
            <Plus size={16} /> Add Holiday
          </button>
        </div>

        {showForm && (
          <div className="card mb-6 max-w-lg">
            <h3 className="font-semibold text-slate-700 mb-4">Add Holiday</h3>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <label className="label">Holiday Name *</label>
                <input value={form.name} onChange={e => setForm(p => ({...p, name: e.target.value}))} className="input" required />
              </div>
              <div>
                <label className="label">Date *</label>
                <input type="date" value={form.date} onChange={e => setForm(p => ({...p, date: e.target.value}))} className="input" required />
              </div>
              <div>
                <label className="label">Description</label>
                <input value={form.description} onChange={e => setForm(p => ({...p, description: e.target.value}))} className="input" />
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={form.is_optional} onChange={e => setForm(p => ({...p, is_optional: e.target.checked}))} />
                Optional Holiday
              </label>
              <button type="submit" className="btn-primary">Save Holiday</button>
            </form>
          </div>
        )}

        <div className="space-y-4">
          {Object.entries(grouped).map(([month, hs]: [string, any]) => (
            <div key={month} className="card">
              <h3 className="font-semibold text-slate-700 mb-3 pb-2 border-b border-slate-100">{month}</h3>
              <div className="space-y-2">
                {hs.map((h: any) => (
                  <div key={h.id} className="flex items-center justify-between py-2">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-[#1a3a5c] rounded-lg flex items-center justify-center text-white text-sm font-bold">
                        {new Date(h.date).getDate()}
                      </div>
                      <div>
                        <p className="font-medium text-slate-800">{h.name}</p>
                        <p className="text-xs text-slate-500">
                          {new Date(h.date).toLocaleDateString('en-IN', { weekday: 'long' })}
                          {h.is_optional && <span className="ml-2 text-amber-600">(Optional)</span>}
                        </p>
                      </div>
                    </div>
                    <button onClick={() => handleDelete(h.id)} className="p-1.5 hover:bg-red-50 rounded text-red-400">
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))}
          {holidays.length === 0 && (
            <div className="card text-center py-12 text-slate-400">
              <Calendar size={32} className="mx-auto mb-2 opacity-30" />
              <p>No holidays defined yet</p>
            </div>
          )}
        </div>
      </Layout>
    </>
  );
}
