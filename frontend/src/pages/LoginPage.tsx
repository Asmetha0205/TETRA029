import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, ArrowRight } from 'lucide-react';
import { PageTransition } from '../components/animation/PageTransition';
import { toast } from 'sonner';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success('Authentication placeholder: Signed in successfully!');
    navigate('/dashboard');
  };

  return (
    <PageTransition>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-extrabold text-foreground tracking-tight">Welcome Back</h2>
          <p className="text-xs text-muted-foreground mt-1">
            Sign in to access your saved curriculum audits and analytics reports.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-muted-foreground block mb-1">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="email"
                defaultValue="dean.engineering@stanford.edu"
                className="w-full h-10 pl-10 pr-3 rounded-xl border border-input bg-card text-xs text-foreground focus:ring-2 focus:ring-primary/40 focus:outline-none"
                required
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs font-semibold text-muted-foreground">Password</label>
              <Link to="/forgot-password" className="text-[11px] text-primary hover:underline">
                Forgot password?
              </Link>
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="password"
                defaultValue="••••••••••••"
                className="w-full h-10 pl-10 pr-3 rounded-xl border border-input bg-card text-xs text-foreground focus:ring-2 focus:ring-primary/40 focus:outline-none"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full h-10 rounded-xl bg-primary text-primary-foreground font-bold text-xs shadow-md hover:opacity-90 transition-opacity flex items-center justify-center space-x-2"
          >
            <span>Sign In to Platform</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </form>

        <div className="text-center text-xs text-muted-foreground">
          Don't have an account?{' '}
          <Link to="/register" className="text-primary font-bold hover:underline">
            Register Demo Account
          </Link>
        </div>
      </div>
    </PageTransition>
  );
};
