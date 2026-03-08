import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../components/common/AuthContext';

export default function Index() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!user) router.push('/login');
      else if (user.role === 'admin' || user.role === 'manager') router.push('/admin/dashboard');
      else router.push('/employee/dashboard');
    }
  }, [user, loading, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#1a3a5c]">
      <div className="text-white text-center">
        <div className="w-12 h-12 border-4 border-white/30 border-t-white rounded-full animate-spin mx-auto mb-4" />
        <p className="font-display font-semibold">CloudHub HR Portal</p>
      </div>
    </div>
  );
}
