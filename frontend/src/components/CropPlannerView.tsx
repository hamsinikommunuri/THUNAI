import React from 'react';
import { 
  Compass, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  Droplets, 
  ShieldCheck, 
  ArrowRight,
  TrendingUp
} from 'lucide-react';
import { CropRecommendationData } from '../types';
import { translations, Language } from '../i18n/translations';

interface CropPlannerViewProps {
  cropRecs: CropRecommendationData | null;
  onSelectCropForDiagnosis: (cropId: string) => void;
  lang: Language;
}

export const CropPlannerView: React.FC<CropPlannerViewProps> = ({
  cropRecs,
  onSelectCropForDiagnosis,
  lang,
}) => {
  const t = translations[lang];

  if (!cropRecs) {
    return <div className="p-12 text-center text-mineral-muted">Evaluating crop suitability matrices...</div>;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-white/10">
        <div>
          <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
            AGRONOMIC SUITABILITY ENGINE
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Seasonal Crop Suitability Matrix ({cropRecs.location})
          </h1>
        </div>
        <div className="text-right text-[11px] font-mono text-mineral-muted">
          <div>Engine: Rule-Based Agronomic System</div>
          <div>Season: {cropRecs.current_season}</div>
        </div>
      </div>

      {/* Environmental Baseline Card */}
      <div className="p-6 rounded-natural-lg bg-gradient-to-r from-carbon via-[#101914] to-carbon border border-white/10 flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="text-[10px] font-mono text-emerald uppercase font-semibold">
            CURRENT METRIC CONTEXT
          </span>
          <p className="text-sm font-bold text-white mt-0.5">
            Evaluating {cropRecs.location} under {cropRecs.current_season}
          </p>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="p-2 rounded-xl bg-black/40">
            <span className="text-mineral-muted block text-[10px]">Temp</span>
            <span className="font-bold text-white">{cropRecs.temperature_c}°C</span>
          </div>
          <div className="p-2 rounded-xl bg-black/40">
            <span className="text-mineral-muted block text-[10px]">Rainfall</span>
            <span className="font-bold text-white">{cropRecs.rainfall_annual_mm} mm</span>
          </div>
          <div className="p-2 rounded-xl bg-black/40">
            <span className="text-mineral-muted block text-[10px]">Soil</span>
            <span className="font-bold text-white">{cropRecs.soil_type}</span>
          </div>
        </div>
      </div>

      {/* Recommendations Cards */}
      <div className="space-y-4">
        {cropRecs.recommended_crops.map((crop) => {
          const isHigh = crop.suitability === 'High';
          return (
            <div
              key={crop.crop_id}
              className={`p-6 rounded-natural-lg border transition-all ${
                isHigh 
                  ? 'bg-[#0E1411] border-emerald/40 shadow-natural' 
                  : 'bg-carbon/70 border-white/10'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-white/5">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-xl font-bold text-white">
                      {lang === 'ta' ? crop.name_ta : crop.name_en}
                    </h3>
                    <span className="text-xs text-mineral-muted font-serif italic">
                      ({crop.scientific_name})
                    </span>
                  </div>
                  <p className="text-xs text-mineral-muted mt-0.5">
                    {crop.economic_importance}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase font-mono ${
                    isHigh 
                      ? 'bg-emerald/20 text-emerald-bright border border-emerald/40' 
                      : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                  }`}>
                    {crop.suitability} Suitability
                  </span>
                  <span className="text-xs font-mono font-bold text-mineral">
                    Score: {crop.suitability_score}/100
                  </span>
                </div>
              </div>

              {/* Rationale List */}
              <div className="my-4 space-y-2">
                <span className="text-[10px] font-mono text-emerald uppercase font-semibold block">
                  Agronomic Justification & Factors:
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  {crop.reasons.map((r, idx) => (
                    <div key={idx} className="flex items-start gap-2 p-2.5 rounded-xl bg-carbon">
                      <CheckCircle2 className="w-4 h-4 text-emerald shrink-0 mt-0.5" />
                      <span className="text-mineral">{r}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick Details & Action */}
              <div className="pt-3 border-t border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-4 text-mineral-muted">
                  <span>Optimal: {crop.ideal_temperature_range}</span>
                  <span>·</span>
                  <span>Water: {crop.water_requirement}</span>
                </div>

                <button
                  onClick={() => onSelectCropForDiagnosis(crop.crop_id)}
                  className="px-4 py-2 rounded-xl bg-white/[0.06] hover:bg-emerald hover:text-obsidian text-mineral font-semibold text-xs transition-all flex items-center justify-center gap-1.5 self-start sm:self-auto"
                >
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Diagnose This Crop</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
};
