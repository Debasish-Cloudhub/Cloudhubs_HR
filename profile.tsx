import { useState } from 'react';
import { useAuth } from '../components/common/AuthContext';
import { Eye, EyeOff, LogIn } from 'lucide-react';
import toast from 'react-hot-toast';
import Head from 'next/head';

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      toast.success('Welcome back!');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>Login — CloudHub HR Portal</title>
      </Head>
      <div className="min-h-screen flex" style={{ background: 'linear-gradient(135deg, #1a3a5c 0%, #0f2544 50%, #1a3a5c 100%)' }}>
        {/* Left panel */}
        <div className="hidden lg:flex flex-col justify-center px-16 flex-1">
          <div className="mb-8">
            <div className="w-14 h-14 bg-[#0ea5e9] rounded-2xl flex items-center justify-center font-display font-bold text-white text-2xl mb-6">
              CH
            </div>
            <h1 className="font-display font-bold text-white text-4xl leading-tight mb-4">
              CloudHub<br />HR Portal
            </h1>
            <p className="text-blue-300 text-lg leading-relaxed max-w-md">
              Streamline your workforce management with our comprehensive HR platform.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4 max-w-sm">
            {[
              ['Employee Management', 'Onboard & manage staff'],
              ['Timesheet Tracking', 'Monitor work hours'],
              ['Salary Processing', 'Automated payroll'],
              ['HR Documents', 'Centralized policies'],
            ].map(([title, desc]) => (
              <div key={title} className="bg-white/10 rounded-xl p-4 backdrop-blur">
                <p className="text-white font-semibold text-sm">{title}</p>
                <p className="text-blue-300 text-xs mt-1">{desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Right panel - login form */}
        <div className="flex items-center justify-center w-full lg:w-auto lg:min-w-[480px] px-6">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
            <div className="lg:hidden mb-6 text-center">
              <div className="w-12 h-12 bg-[#1a3a5c] rounded-xl flex items-center justify-center font-display font-bold text-white text-lg mx-auto mb-3">
                CH
              </div>
              <h2 className="font-display font-bold text-[#1a3a5c] text-2xl">CloudHub HR Portal</h2>
            </div>

            <h2 className="hidden lg:block font-display font-bold text-[#1a3a5c] text-2xl mb-1">Welcome back</h2>
            <p className="text-slate-500 text-sm mb-8">Sign in to your account to continue</p>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="label">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="you@cloudhub.in"
                  className="input"
                  required
                  autoComplete="email"
                />
              </div>
              <div>
                <label className="label">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="input pr-10"
                    required
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full btn-primary justify-center py-3 text-base"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Signing in...
                  </span>
                ) : (
                  <span className="flex items-center gap-2 justify-center">
                    <LogIn size={16} /> Sign In
                  </span>
                )}
              </button>
            </form>

            <div className="mt-6 pt-6 border-t border-slate-100">
              <p className="text-xs text-slate-400 text-center mb-3">Demo credentials</p>
              <div className="space-y-1.5">
                {[
                  { role: 'Admin', email: 'admin@cloudhub.in', pwd: 'Admin@123', color: 'bg-purple-50 text-purple-700' },
                  { role: 'Employee', email: 'john.doe@cloudhub.in', pwd: 'Employee@123', color: 'bg-blue-50 text-blue-700' },
                  { role: 'Manager', email: 'manager@cloudhub.in', pwd: 'Manager@123', color: 'bg-green-50 text-green-700' },
                ].map(({ role, email: e, pwd, color }) => (
                  <button
                    key={role}
                    type="button"
                    onClick={() => { setEmail(e); setPassword(pwd); }}
                    className={`w-full text-left text-xs px-3 py-2 rounded-lg ${color} font-medium`}
                  >
                    <span className="font-semibold">{role}:</span> {e}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
