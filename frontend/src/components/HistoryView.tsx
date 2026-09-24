import React from 'react';
import { 
  History as HistoryIcon, 
  Sprout, 
  Clock, 
  CheckCircle2, 
  AlertTriangle, 
  ChevronRight,
  ShieldCheck
} from 'lucide-react';
import { HistoryItem } from '../types';
import { translations, Language } from '../i18n/translations';

interface HistoryViewProps {
  history: HistoryItem[];
  onSelectHistoryItem: (item: HistoryItem) => void;
  lang: Language;
}

export const HistoryView: React.FC<HistoryViewProps> = ({ history, onSelectHistoryItem, lang }) => {
  const t = translations[lang];

  return (
    <div className="space-y-8 animate-in fade-in duration-300 pb-12">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-white/10">
        <div>
          <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
            LONGITUDINAL DIAGNOSIS LOG
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Diagnosis & Treatment History
          </h1>
        </div>
        <span className="text-xs font-mono text-emerald">
          {history.length} Scans Recorded
        </span>
      </div>

      {history.length === 0 ? (
        <div className="p-12 text-center rounded-natural-lg bg-carbon/50 border border-white/10 space-y-3">
          <HistoryIcon className="w-10 h-10 text-mineral-muted mx-auto" />
          <p className="text-sm font-semibold text-white">No Previous Field Diagnoses</p>
          <p className="text-xs text-mineral-muted max-w-sm mx-auto">
            Uploaded crop leaf diagnoses will be saved here automatically for tracking disease progression.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {history.map((item) => (
            <div
              key={item.id}
              onClick={() => onSelectHistoryItem(item)}
              className="p-5 rounded-2xl bg-[#0E1411] hover:bg-carbon border border-white/10 hover:border-emerald/40 transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4 group"
            >
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-2xl bg-carbon flex items-center justify-center text-emerald overflow-hidden border border-white/10 shrink-0">
                  {item.image_url ? (
                    <img src={item.image_url} alt={item.disease_name} className="w-full h-full object-cover" />
                  ) : (
                    <Sprout className="w-7 h-7" />
                  )}
                </div>

                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono uppercase font-bold text-emerald">
                      {item.crop}
                    </span>
                    <span className="text-white/20">·</span>
                    <span className="text-[11px] text-mineral-muted">
                      {item.location_district || 'Detected Field'}
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-white group-hover:text-emerald transition-colors">
                    {item.disease_name}
                  </h3>
                  {item.scientific_name && (
                    <p className="text-xs text-mineral-muted font-serif italic">
                      {item.scientific_name}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-4 self-end sm:self-auto">
                <div className="text-right">
                  <span className="text-[10px] font-mono text-mineral-muted uppercase block">Confidence</span>
                  <span className="text-sm font-bold text-emerald font-mono">
                    {Math.round(item.confidence * 100)}%
                  </span>
                </div>

                {item.spray_recommendation && (
                  <span className={`px-2.5 py-1 rounded-full text-[10px] font-mono font-bold uppercase ${
                    item.spray_recommendation === 'SPRAY NOW' ? 'bg-emerald/20 text-emerald' : 'bg-amber-500/20 text-amber-300'
                  }`}>
                    {item.spray_recommendation}
                  </span>
                )}

                <div className="text-right text-[10px] font-mono text-mineral-muted w-24">
                  {item.created_at}
                </div>

                <ChevronRight className="w-4 h-4 text-mineral-muted group-hover:text-emerald group-hover:translate-x-1 transition-all" />
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
};
