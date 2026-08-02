import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Building, ArrowRight } from 'lucide-react';
import { PageTransition } from '../components/animation/PageTransition';
import { toast } from 'sonner';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success('Registration placeholder: Account created!');
    navigate('/dashboard');
  };

  return (
    <PageTransition>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-extrabold text-foreground tracking-tight">Create Academic Account</h2>
          <p className="text-xs text-muted-foreground mt-1">
            Register your department to start analyzing computer science curricula.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="text-xs font-semibold text-muted-foreground block mb-1">Full Name</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Dr. Alan Turing"
                className="w-full h-10 pl-10 pr-3 rounded-xl border border-input bg-card text-xs text-foreground focus:ring-2 focus:ring-primary/40 focus:outline-none"
                required
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground block mb-1">University / Organization</label>
            <div className="relative">
              <Building className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Stanford University"
                className="w-full h-10 pl-10 pr-3 rounded-xl border border-input bg-card text-xs text-foreground focus:ring-2 focus:ring-primary/40 focus:outline-none"
                required
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground block mb-1">Academic Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="email"
                placeholder="professor@university.edu"
                className="w-full h-10 pl-10 pr-3 rounded-xl border border-input bg-card text-xs text-foreground focus:ring-2 focus:ring-primary/40 focus:outline-none"
                required
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground block mb-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="password"
                placeholder="••••••••••••"
                className="w-full h-10 pl-10 pr-3 rounded-xl border border-input bg-card text-xs text-foreground focus:ring-2 focus:ring-primary/40 focus:outline-none"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full h-10 rounded-xl bg-primary text-primary-foreground font-bold text-xs shadow-md hover:opacity-90 transition-opacity flex items-center justify-center space-x-2"
          >
            <span>Create Account & Continue</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </form>

        <div className="text-center text-xs text-muted-foreground">
          Already registered?{' '}
          <Link to="/login" className="text-primary font-bold hover:underline">
            Sign In Here
          </Link>
        </div>
      </div>
    </PageTransition>
  );
};
