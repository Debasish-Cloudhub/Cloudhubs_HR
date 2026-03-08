import { useEffect, useState } from 'react';
import Layout from '../../components/common/Layout';
import { useAuth } from '../../components/common/AuthContext';
import { getAdminDashboard } from '../../services/api';
import { Users, Clock, Calendar, TrendingUp, Building2 } from 'lucide-react';
import { useRouter } from 'next/router';
import Head from 'next/head';

export default function AdminDashboard() {
  const { user, isAdmin, isManager, loading } = useAuth();
  const router = useRouter();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    if (!loading && !user) router.push('/login');
    if (!loading && user && user.role === 'employee') router.push('/employee/dashboard');
  }, [user, loading]);

  useEffect(() => {
    if (user && (isAdmin || isManager)) {
      getAdminDashboard().then(r => setData(r.data)).catch(() => {});
    }
  }, [user]);

  if (!data) return (
    <Layout>
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-[#1a3a5c]/20 border-t-[#1a3a5c] rounded-full animate-spin" />
      </div>
    </Layout>
  );

  const stats = [
    { label: 'Total Employees', value: data.total_employees, icon: Users, color: 'bg-blue-50 text-blue-600' },
    { label: 'Pending Timesheets', value: data.pending_timesheets, icon: Clock, color: 'bg-amber-50 text-amber-600' },
    { label: 'Upcoming Holidays', value: data.upcoming_holidays?.length || 0, icon: Calendar, color: 'bg-green-50 text-green-600' },
    { label: 'Departments', value: data.department_breakdown?.length || 0, icon: Building2, color: 'bg-purple-50 text-purple-600' },
  ];

  return (
    <>
      <Head><title>Dashboard — CloudHub HR</title></Head>
      <Layout>
        <div className="mb-6">
          <h1 className="font-display font-bold text-2xl text-slate-800">HR Dashboard</h1>
          <p className="text-slate-500 text-sm mt-1">Welcome back, {user?.name}</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {stats.map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="card">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm text-slate-500 font-medium">{label}</p>
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${color}`}>
                  <Icon size={18} />
                </div>
              </div>
              <p className="text-3xl font-display font-bold text-slate-800">{value}</p>
            </div>
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Department Breakdown */}
          <div className="card">
            <h3 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
              <TrendingUp size={16} className="text-[#1a3a5c]" />
              Department Breakdown
            </h3>
            <div className="space-y-2">
              {data.department_breakdown?.map((d: any) => (
                <div key={d.department} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                  <span className="text-sm text-slate-600">{d.department}</span>
                  <span className="text-sm font-semibold text-[#1a3a5c]">{d.count}</span>
                </div>
              ))}
              {(!data.department_breakdown || data.department_breakdown.length === 0) && (
                <p className="text-sm text-slate-400 text-center py-4">No data available</p>
              )}
            </div>
          </div>

          {/* Upcoming Holidays */}
          <div className="card">
            <h3 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
              <Calendar size={16} className="text-[#1a3a5c]" />
              Upcoming Holidays
            </h3>
            <div className="space-y-2">
              {data.upcoming_holidays?.slice(0, 5).map((h: any) => (
                <div key={h.id} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                  <div>
                    <p className="text-sm font-medium text-slate-700">{h.name}</p>
                    {h.is_optional && <span className="text-xs text-slate-400">Optional</span>}
                  </div>
                  <span className="text-xs text-slate-500 bg-slate-100 px-2 py-1 rounded">
                    {new Date(h.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                  </span>
                </div>
              ))}
              {(!data.upcoming_holidays || data.upcoming_holidays.length === 0) && (
                <p className="text-sm text-slate-400 text-center py-4">No upcoming holidays</p>
              )}
            </div>
          </div>

          {/* Recent Timesheets */}
          <div className="card lg:col-span-2">
            <h3 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
              <Clock size={16} className="text-[#1a3a5c]" />
              Recent Timesheet Activity
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="text-left py-2 text-xs font-semibold text-slate-500 uppercase tracking-wide">Date</th>
                    <th className="text-left py-2 text-xs font-semibold text-slate-500 uppercase tracking-wide">Project</th>
                    <th className="text-left py-2 text-xs font-semibold text-slate-500 uppercase tracking-wide">Hours</th>
                    <th className="text-left py-2 text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_timesheets?.map((ts: any) => (
                    <tr key={ts.id} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="py-2.5 text-slate-600">{new Date(ts.date).toLocaleDateString('en-IN')}</td>
                      <td className="py-2.5 text-slate-700 font-medium">{ts.project_name}</td>
                      <td className="py-2.5 text-slate-600">{ts.hours_worked}h</td>
                      <td className="py-2.5">
                        <span className={`badge-${ts.status}`}>{ts.status}</span>
                      </td>
                    </tr>
                  ))}
                  {(!data.recent_timesheets || data.recent_timesheets.length === 0) && (
                    <tr><td colSpan={4} className="text-center text-slate-400 py-6">No timesheet data</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
}
