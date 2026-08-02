import { UnifiedAnalysisResult } from '../types/api';

export const exportService = {
  exportJSON(data: UnifiedAnalysisResult, filename = 'curricualign_analysis_report.json') {
    const jsonString = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  },

  exportMarkdown(data: UnifiedAnalysisResult, filename = 'curricualign_analysis_report.md') {
    let md = `# Executive Curriculum Alignment Report\n\n`;
    md += `**University:** ${data.university_name || 'N/A'}\n`;
    md += `**Department:** ${data.department || 'N/A'}\n`;
    md += `**Year:** ${data.curriculum_year || 'N/A'}\n`;
    md += `**Alignment Score:** ${data.alignment_score}%\n`;
    md += `**Generated At:** ${new Date(data.generated_at).toLocaleString()}\n\n`;

    md += `## 1. Summary of Gaps\n\n`;
    data.gap_skills.forEach((gap, idx) => {
      md += `### ${idx + 1}. ${gap.matched_industry_skill} [Priority: ${gap.priority}]\n`;
      md += `- **Category:** ${gap.category}\n`;
      md += `- **Industry Demand Score:** ${gap.industry_demand_score}/100\n`;
      md += `- **Academic Evidence:** ${gap.academic_evidence}\n`;
      md += `- **Industry Evidence:** ${gap.industry_evidence}\n\n`;
    });

    md += `## 2. Recommendations\n\n`;
    data.recommendations.forEach((rec, idx) => {
      md += `### ${idx + 1}. ${rec.technology} [${rec.priority}]\n`;
      md += `- **Suggested Course:** ${rec.suggested_course}\n`;
      md += `- **Reason:** ${rec.reason}\n`;
      md += `- **Hands-on Lab:** ${rec.hands_on_lab}\n`;
      md += `- **Mini Project:** ${rec.mini_project}\n\n`;
    });

    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  },

  exportPrintableHTML(data: UnifiedAnalysisResult) {
    window.print();
  },
};
