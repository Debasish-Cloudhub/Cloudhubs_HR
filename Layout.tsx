import { useEffect, useState } from 'react';
import Layout from '../../components/common/Layout';
import { getEmployees, deactivateEmployee } from '../../services/api';
import { Users, Search, Plus, Eye, UserX } from 'lucide-react';
import Link from 'next/link';
import toast from 'react-hot-toast';
import Head from 'next/head';

const TYPE_COLORS: Record<string, string> = {
  permanent: 'bg-blue-100 text-blue-700',
  contractor: 'bg-orange-100 text-orange-700',
  intern: 'bg-green-100 text-green-700',
  consultant: 'bg-purple-100 text-purple-700',
};

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchEmployees = async () => {
    setLoading(true);
    try {
      const res = await getEmployees({ search: search || undefined });
      setEmployees(res.data);
    } catch { toast.error('Failed to load employees'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchEmployees(); }, [search]);

  const handleDeactivate = async (id: number, name: string) => {
    if (!confirm(`Deactivate ${name}?`)) return;
    try {
      await deactivateEmployee(id);
      toast.success('Employee deactivated');
      fetchEmployees();
    } catch { toast.error('Failed'); }
  };

  return (
    <>
      <Head><title>Employees — CloudHub HR</title></Head>
      <Layout>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="font-display font-bold text-2xl text-slate-800">Employees</h1>
            <p className="text-slate-500 text-sm mt-1">{employees.length} active employees</p>
          </div>
          <Link href="/admin/onboarding" className="btn-primary">
            <Plus size={16} /> Add Employee
          </Link>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="relative flex-1 max-w-xs">
              <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search employees..."
                className="input pl-9"
              />
            </div>
          </div>

          {loading ? (
            <div className="flex justify-center py-12">
              <div className="w-8 h-8 border-4 border-[#1a3a5c]/20 border-t-[#1a3a5c] rounded-full animate-spin" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200">
                    {['Employee ID', 'Name', 'Department', 'Designation', 'Type', 'Joined', 'Actions'].map(h => (
                      <th key={h} className="text-left py-3 px-2 text-xs font-semibold text-slate-500 uppercase tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {employees.map(emp => (
                    <tr key={emp.id} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="py-3 px-2 font-mono text-xs text-slate-600">{emp.employee_id}</td>
                      <td className="py-3 px-2 font-medium text-slate-800">{emp.full_name}</td>
                      <td className="py-3 px-2 text-slate-600">{emp.department || '—'}</td>
                      <td className="py-3 px-2 text-slate-600">{emp.designation || '—'}</td>
                      <td className="py-3 px-2">
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TYPE_COLORS[emp.employment_type] || ''}`}>
                          {emp.employment_type}
                        </span>
                      </td>
                      <td className="py-3 px-2 text-slate-500">
                        {emp.date_of_joining ? new Date(emp.date_of_joining).toLocaleDateString('en-IN') : '—'}
                      </td>
                      <td className="py-3 px-2">
                        <div className="flex items-center gap-2">
                          <Link
                            href={`/admin/employees/${emp.id}`}
                            className="p-1.5 rounded hover:bg-blue-50 text-blue-600"
                            title="View"
                          >
                            <Eye size={14} />
                          </Link>
                          <button
                            onClick={() => handleDeactivate(emp.id, emp.full_name)}
                            className="p-1.5 rounded hover:bg-red-50 text-red-500"
                            title="Deactivate"
                          >
                            <UserX size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {employees.length === 0 && (
                    <tr><td colSpan={7} className="text-center text-slate-400 py-10">No employees found</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Layout>
    </>
  );
}
