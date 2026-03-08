import { useEffect, useState, useRef } from 'react';
import Layout from '../../components/common/Layout';
import { getDocuments, uploadDocument, deleteDocument, downloadDocument } from '../../services/api';
import { FileText, Upload, Trash2, Download } from 'lucide-react';
import toast from 'react-hot-toast';
import Head from 'next/head';

const CATEGORIES = ['HR Policy', 'Employee Handbook', 'Leave Policy', 'Code of Conduct', 'Other'];

export default function AdminDocumentsPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', category: '' });
  const fileRef = useRef<HTMLInputElement>(null);
  const [showForm, setShowForm] = useState(false);

  const fetch = async () => {
    try { const r = await getDocuments(); setDocuments(r.data); } catch {}
  };
  useEffect(() => { fetch(); }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file) return toast.error('Select a file');
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append('title', form.title);
      fd.append('description', form.description);
      fd.append('category', form.category);
      fd.append('file', file);
      await uploadDocument(fd);
      toast.success('Document uploaded');
      setForm({ title: '', description: '', category: '' });
      if (fileRef.current) fileRef.current.value = '';
      setShowForm(false);
      fetch();
    } catch { toast.error('Upload failed'); }
    finally { setUploading(false); }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete document?')) return;
    try { await deleteDocument(id); toast.success('Deleted'); fetch(); } catch {}
  };

  const handleDownload = async (id: number, filename: string) => {
    try {
      const res = await downloadDocument(id);
      const url = URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a'); a.href = url; a.download = filename; a.click();
      URL.revokeObjectURL(url);
    } catch { toast.error('Download failed'); }
  };

  return (
    <>
      <Head><title>Documents — CloudHub HR</title></Head>
      <Layout>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="font-display font-bold text-2xl text-slate-800">HR Documents</h1>
            <p className="text-slate-500 text-sm">{documents.length} documents</p>
          </div>
          <button onClick={() => setShowForm(!showForm)} className="btn-primary">
            <Upload size={16} /> Upload Document
          </button>
        </div>

        {showForm && (
          <div className="card mb-6 max-w-lg">
            <h3 className="font-semibold text-slate-700 mb-4">Upload Document</h3>
            <form onSubmit={handleUpload} className="space-y-3">
              <div>
                <label className="label">Title *</label>
                <input value={form.title} onChange={e => setForm(p => ({...p, title: e.target.value}))} className="input" required />
              </div>
              <div>
                <label className="label">Category</label>
                <select value={form.category} onChange={e => setForm(p => ({...p, category: e.target.value}))} className="input">
                  <option value="">Select category</option>
                  {CATEGORIES.map(c => <option key={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Description</label>
                <input value={form.description} onChange={e => setForm(p => ({...p, description: e.target.value}))} className="input" />
              </div>
              <div>
                <label className="label">File *</label>
                <input ref={fileRef} type="file" className="input" accept=".pdf,.doc,.docx,.xlsx,.pptx" />
              </div>
              <button type="submit" disabled={uploading} className="btn-primary">
                {uploading ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <><Upload size={14} /> Upload</>}
              </button>
            </form>
          </div>
        )}

        <div className="card">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {documents.map(doc => (
              <div key={doc.id} className="border border-slate-200 rounded-xl p-4 hover:border-[#1a3a5c]/30 transition-all">
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 bg-[#eff6ff] rounded-lg flex items-center justify-center">
                    <FileText size={18} className="text-[#1a3a5c]" />
                  </div>
                  <div className="flex gap-1">
                    <button onClick={() => handleDownload(doc.id, doc.filename)} className="p-1.5 hover:bg-blue-50 rounded text-blue-600">
                      <Download size={13} />
                    </button>
                    <button onClick={() => handleDelete(doc.id)} className="p-1.5 hover:bg-red-50 rounded text-red-400">
                      <Trash2 size={13} />
                    </button>
                  </div>
                </div>
                <p className="font-semibold text-slate-800 text-sm mb-1">{doc.title}</p>
                {doc.category && (
                  <span className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">{doc.category}</span>
                )}
                <p className="text-xs text-slate-400 mt-2">
                  {new Date(doc.created_at).toLocaleDateString('en-IN')}
                </p>
              </div>
            ))}
            {documents.length === 0 && (
              <div className="col-span-3 text-center py-12 text-slate-400">
                <FileText size={32} className="mx-auto mb-2 opacity-30" />
                <p>No documents uploaded yet</p>
              </div>
            )}
          </div>
        </div>
      </Layout>
    </>
  );
}
