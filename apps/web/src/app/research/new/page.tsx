import { ResearchForm } from '@/components/research/ResearchForm';

export default function NewResearchPage() {
  return (
    <div className="max-w-4xl mx-auto py-8 space-y-8 animate-fade-in">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Initialize Research</h1>
        <p className="text-muted-foreground">
          Configure the parameters for your autonomous research run. The more specific your question, the better the results.
        </p>
      </div>

      <ResearchForm />
    </div>
  );
}
