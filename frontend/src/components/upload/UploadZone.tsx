import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Building2, Calendar, BookOpen, ArrowRight } from 'lucide-react';
import { apiService } from '../../services/api';
import { useAppStore } from '../../app/store';
import { toast } from 'sonner';

export const UploadZone: React.FC = () => {
  const navigate = useNavigate();
  const { setActiveAnalysis, addAnalysisToHistory } = useAppStore();

  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [universityName, setUniversityName] = useState('Stanford University School of Engineering');
  const [curriculumYear, setCurriculumYear] = useState('2025-2026');
  const [department, setDepartment] = useState('Department of Computer Science');
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateFile = (file: File): boolean => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Invalid file format. Please upload a PDF curriculum document.');
      return false;
    }
    if (file.size > 15 * 1024 * 1024) {
      toast.error('File size exceeds 15 MB limit.');
      return false;
    }
    return true;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
        toast.success(`Selected file: ${file.name}`);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
        toast.success(`Selected file: ${file.name}`);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      toast.error('Please select or drag a PDF curriculum document first.');
      return;
    }

    setIsUploading(true);
    setProgress(15);

    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(interval);
          return 90;
        }
        return prev + 15;
      });
    }, 300);

    try {
      const res = await apiService.analyzeCurriculum(selectedFile, universityName, curriculumYear, department);
      clearInterval(interval);
      setProgress(100);

      if (res.success && res.data) {
        setActiveAnalysis(res.data);
        addAnalysisToHistory(res.data);
        toast.success('Curriculum uploaded & analysis initiated!');
        setTimeout(() => {
          navigate(`/analysis/${res.data.analysis_id}/progress`);
        }, 500);
      } else {
        toast.error('Upload failed: ' + res.message);
      }
    } catch (err: any) {
      clearInterval(interval);
      toast.error('Analysis error: ' + (err?.message || 'Server error'));
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Upload Box Form */}
      <form onSubmit={handleSubmit} className="rounded-3xl border border-border/60 bg-card p-6 md:p-8 shadow-xl relative overflow-hidden">
        <h2 className="text-xl font-bold text-foreground mb-1 flex items-center gap-2">
          <UploadCloud className="h-6 w-6 text-primary" />
          <span>Curriculum PDF Analysis Portal</span>
        </h2>
        <p className="text-xs text-muted-foreground mb-6">
          Upload an official Computer Science course syllabus or curriculum PDF to trigger single-call end-to-end vector matching and graph alignment.
        </p>

        {/* Metadata Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5 mb-1.5">
              <Building2 className="h-3.5 w-3.5 text-primary" />
              <span>University Name</span>
            </label>
            <input
              type="text"
              value={universityName}
              onChange={(e) => setUniversityName(e.target.value)}
              placeholder="e.g. Stanford University"
              className="w-full h-10 px-3 text-xs rounded-xl border border-input bg-secondary/40 text-foreground focus:ring-2 focus:ring-primary/40 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5 mb-1.5">
              <Calendar className="h-3.5 w-3.5 text-primary" />
              <span>Academic Year</span>
            </label>
            <input
              type="text"
              value={curriculumYear}
              onChange={(e) => setCurriculumYear(e.target.value)}
              placeholder="2025-2026"
              className="w-full h-10 px-3 text-xs rounded-xl border border-input bg-secondary/40 text-foreground focus:ring-2 focus:ring-primary/40 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5 mb-1.5">
              <BookOpen className="h-3.5 w-3.5 text-primary" />
              <span>Department</span>
            </label>
            <input
              type="text"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              placeholder="Computer Science"
              className="w-full h-10 px-3 text-xs rounded-xl border border-input bg-secondary/40 text-foreground focus:ring-2 focus:ring-primary/40 focus:outline-none"
              required
            />
          </div>
        </div>

        {/* Drag & Drop Zone */}
        <div
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          className={`relative flex flex-col items-center justify-center p-8 md:p-12 border-2 border-dashed rounded-2xl transition-all cursor-pointer ${
            dragActive
              ? 'border-primary bg-primary/10 scale-[1.01]'
              : selectedFile
              ? 'border-emerald-500/50 bg-emerald-500/5'
              : 'border-border/80 hover:border-primary/50 bg-secondary/20 hover:bg-secondary/40'
          }`}
        >
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />

          {selectedFile ? (
            <div className="flex flex-col items-center text-center space-y-2">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500/10 text-emerald-500 border border-emerald-500/30">
                <FileText className="h-7 w-7" />
              </div>
              <p className="text-sm font-bold text-foreground">{selectedFile.name}</p>
              <p className="text-xs text-muted-foreground">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Ready for Analysis
              </p>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedFile(null);
                }}
                className="text-xs text-rose-500 underline hover:text-rose-600 mt-1"
              >
                Remove File
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center text-center space-y-3">
              <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-primary/10 text-primary border border-primary/20 shadow-inner">
                <UploadCloud className="h-8 w-8 animate-bounce" />
              </div>
              <div>
                <p className="text-sm font-bold text-foreground">
                  Click to upload or drag & drop curriculum PDF
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Supports official PDF syllabus documents (Max 15MB)
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Progress Bar */}
        {isUploading && (
          <div className="mt-4 space-y-1.5">
            <div className="flex justify-between text-xs text-muted-foreground font-medium">
              <span>Uploading & Validating Document...</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-secondary overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="mt-6 flex justify-end">
          <button
            type="submit"
            disabled={!selectedFile || isUploading}
            className="inline-flex items-center space-x-2 h-11 px-6 rounded-xl bg-gradient-to-r from-primary to-accent text-white font-semibold text-sm shadow-lg shadow-primary/25 hover:opacity-95 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none transition-all"
          >
            <span>Run Autonomous Analysis</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </form>
    </div>
  );
};
