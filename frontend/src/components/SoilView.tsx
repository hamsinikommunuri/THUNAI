import React, { useState } from 'react';
import { 
  Layers, 
  AlertCircle, 
  FlaskConical, 
  CheckCircle2, 
  ExternalLink, 
  Info,
  Loader2,
  FileCheck
} from 'lucide-react';
import { SoilProfile, SoilLabInputs } from '../types';
import { translations, Language } from '../i18n/translations';
import { ThunaiApiClient } from '../api/client';

interface SoilViewProps {
  soil: SoilProfile | null;
  onSoilUpdated: (newProfile: SoilProfile) => void;
  lang: Language;
}

export const SoilView: React.FC<SoilViewProps> = ({ soil, onSoilUpdated, lang }) => {
  const t = translations[lang];

  const [modalOpen, setModalOpen] = useState(false);
  const [inputs, setInputs] = useState<SoilLabInputs>({
    ph: 7.2,
    nitrogen_kg_ha: 290,
    phosphorus_kg_ha: 18,
    potassium_kg_ha: 310,
    organic_carbon_percent: 0.65,
    soil_type: 'Clay Loam',
    soil_moisture_percent: 24
  });
  const [submitting, setSubmitting] = useState(false);

  if (!soil) {
    return <div className="p-12 text-center text-mineral-muted">Loading regional pedological profiles...</div>;
  }

  const isLabVerified = soil.data_type === 'USER_MEASUREMENT';

  const handleSubmitMeasurements = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const updated = await ThunaiApiClient.evaluateSoilMeasurements(soil.district, inputs);
      onSoilUpdated(updated);
      setModalOpen(false);
    } catch (err) {
      console.error('Failed to submit soil test:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
        <div>
          <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
            PEDOLOGICAL INTELLIGENCE
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Soil Health Profile ({soil.district} District)
          </h1>
        </div>

        <button
          onClick={() => setModalOpen(true)}
          className="px-5 py-2.5 rounded-2xl bg-emerald hover:bg-emerald-bright text-obsidian font-bold text-xs flex items-center gap-2 transition-all shadow-md self-start sm:self-auto"
        >
          <FlaskConical className="w-4 h-4" />
          <span>{t.enterLabTest}</span>
        </button>
      </div>

      {/* Provenance Badge & Statutory Caution */}
      <div className={`p-4 sm:p-5 rounded-2xl border flex items-start gap-3 ${
        isLabVerified
          ? 'bg-emerald/10 border-emerald/40 text-emerald-100'
          : 'bg-amber-950/40 border-amber-500/40 text-amber-200'
      }`}>
        {isLabVerified ? (
          <CheckCircle2 className="w-5 h-5 text-emerald shrink-0 mt-0.5" />
        ) : (
          <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        )}
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs font-bold uppercase tracking-wider">
              {soil.data_type === 'USER_MEASUREMENT' ? 'VERIFIED USER SOIL HEALTH CARD TEST' : 'REGIONAL ESTIMATE'}
            </span>
          </div>
          <p className="text-xs leading-relaxed text-mineral">
            {soil.warning_notice}
          </p>
        </div>
      </div>

      {/* Main Soil Characteristic Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        
        {/* Physical Taxonomy Card */}
        <div className="p-6 rounded-natural-lg bg-[#0E1411] border border-white/10 space-y-4 shadow-natural">
          <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
            SOIL PHYSICAL PROPERTIES
          </span>

          <div className="space-y-3">
            <div className="p-3.5 rounded-xl bg-carbon">
              <span className="text-[10px] font-mono text-mineral-muted uppercase block">Dominant Regional Soil</span>
              <p className="text-base font-bold text-white mt-0.5">{soil.dominant_soil_type}</p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3.5 rounded-xl bg-carbon">
                <span className="text-[10px] font-mono text-mineral-muted uppercase block">Soil Texture</span>
                <p className="text-xs font-semibold text-mineral mt-0.5">{soil.texture}</p>
              </div>
              <div className="p-3.5 rounded-xl bg-carbon">
                <span className="text-[10px] font-mono text-mineral-muted uppercase block">Drainage Class</span>
                <p className="text-xs font-semibold text-mineral mt-0.5">{soil.drainage}</p>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-carbon text-xs text-mineral-muted leading-relaxed">
              <strong className="text-mineral font-medium">Horizon Characteristics: </strong>
              {soil.regional_characteristics}
            </div>
          </div>
        </div>

        {/* Chemical Fertility (pH & NPK) */}
        <div className="p-6 rounded-natural-lg bg-[#0E1411] border border-white/10 space-y-4 shadow-natural">
          <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
            CHEMICAL NUTRIENT STATUS (N-P-K)
          </span>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3.5 rounded-xl bg-carbon">
              <span className="text-[10px] font-mono text-mineral-muted uppercase block">pH Range</span>
              <p className="text-xl font-extrabold text-emerald mt-0.5">{soil.ph_range}</p>
              <span className="text-[10px] text-mineral-muted block">{soil.ph_category}</span>
            </div>

            <div className="p-3.5 rounded-xl bg-carbon">
              <span className="text-[10px] font-mono text-mineral-muted uppercase block">Organic Carbon</span>
              <p className="text-xl font-extrabold text-white mt-0.5">{soil.organic_carbon}</p>
              <span className="text-[10px] text-mineral-muted block">Microbial humus index</span>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="p-3 rounded-xl bg-carbon">
              <span className="text-[9px] font-mono text-emerald uppercase font-bold block">Nitrogen (N)</span>
              <span className="text-xs font-bold text-white block mt-1">{soil.nitrogen_condition}</span>
            </div>
            <div className="p-3 rounded-xl bg-carbon">
              <span className="text-[9px] font-mono text-emerald uppercase font-bold block">Phosphorus (P)</span>
              <span className="text-xs font-bold text-white block mt-1">{soil.phosphorus_condition}</span>
            </div>
            <div className="p-3 rounded-xl bg-carbon">
              <span className="text-[9px] font-mono text-emerald uppercase font-bold block">Potassium (K)</span>
              <span className="text-xs font-bold text-white block mt-1">{soil.potassium_condition}</span>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-carbon text-xs text-mineral-muted leading-relaxed">
            <strong className="text-mineral font-medium">Agronomic Advisory: </strong>
            {soil.management_advice}
          </div>
        </div>

      </div>

      {/* Modal: Soil Health Card Measurement Entry */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian/80 backdrop-blur-md animate-in fade-in duration-150">
          <div className="relative w-full max-w-lg bg-[#0F1411] border border-white/10 rounded-natural-lg p-6 shadow-natural-dark space-y-4">
            
            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <div className="flex items-center gap-2 text-emerald">
                <FileCheck className="w-5 h-5" />
                <h3 className="text-base font-bold text-white">Enter Real Soil Health Card Test</h3>
              </div>
              <button onClick={() => setModalOpen(false)} className="text-mineral-muted hover:text-white text-xs">
                ✕
              </button>
            </div>

            <p className="text-xs text-mineral-muted leading-relaxed">
              If you have an official laboratory Soil Health Card test from your KVK or district lab, enter it here. 
              THUNAI will immediately override regional averages and tailor nutrient advice.
            </p>

            <form onSubmit={handleSubmitMeasurements} className="space-y-3 pt-2">
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="text-[10px] font-mono text-mineral-muted uppercase block mb-1">Soil pH (0 - 14)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="3"
                    max="11"
                    value={inputs.ph || ''}
                    onChange={(e) => setInputs({ ...inputs, ph: parseFloat(e.target.value) })}
                    className="w-full p-2.5 rounded-xl bg-carbon border border-white/10 text-white focus:outline-none focus:border-emerald"
                  />
                </div>

                <div>
                  <label className="text-[10px] font-mono text-mineral-muted uppercase block mb-1">Organic Carbon (%)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={inputs.organic_carbon_percent || ''}
                    onChange={(e) => setInputs({ ...inputs, organic_carbon_percent: parseFloat(e.target.value) })}
                    className="w-full p-2.5 rounded-xl bg-carbon border border-white/10 text-white focus:outline-none focus:border-emerald"
                  />
                </div>

                <div>
                  <label className="text-[10px] font-mono text-mineral-muted uppercase block mb-1">Nitrogen (kg/ha)</label>
                  <input
                    type="number"
                    value={inputs.nitrogen_kg_ha || ''}
                    onChange={(e) => setInputs({ ...inputs, nitrogen_kg_ha: parseFloat(e.target.value) })}
                    className="w-full p-2.5 rounded-xl bg-carbon border border-white/10 text-white focus:outline-none focus:border-emerald"
                  />
                </div>

                <div>
                  <label className="text-[10px] font-mono text-mineral-muted uppercase block mb-1">Phosphorus (kg/ha)</label>
                  <input
                    type="number"
                    value={inputs.phosphorus_kg_ha || ''}
                    onChange={(e) => setInputs({ ...inputs, phosphorus_kg_ha: parseFloat(e.target.value) })}
                    className="w-full p-2.5 rounded-xl bg-carbon border border-white/10 text-white focus:outline-none focus:border-emerald"
                  />
                </div>

                <div>
                  <label className="text-[10px] font-mono text-mineral-muted uppercase block mb-1">Potassium (kg/ha)</label>
                  <input
                    type="number"
                    value={inputs.potassium_kg_ha || ''}
                    onChange={(e) => setInputs({ ...inputs, potassium_kg_ha: parseFloat(e.target.value) })}
                    className="w-full p-2.5 rounded-xl bg-carbon border border-white/10 text-white focus:outline-none focus:border-emerald"
                  />
                </div>

                <div>
                  <label className="text-[10px] font-mono text-mineral-muted uppercase block mb-1">Soil Texture / Type</label>
                  <input
                    type="text"
                    value={inputs.soil_type || ''}
                    onChange={(e) => setInputs({ ...inputs, soil_type: e.target.value })}
                    placeholder="e.g. Red Loam, Clay Loam"
                    className="w-full p-2.5 rounded-xl bg-carbon border border-white/10 text-white focus:outline-none focus:border-emerald"
                  />
                </div>
              </div>

              <div className="pt-3 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-white/5 text-xs text-mineral hover:bg-white/10"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 rounded-xl bg-emerald text-obsidian font-bold text-xs hover:bg-emerald-bright transition-colors flex items-center gap-1.5"
                >
                  {submitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : null}
                  <span>{t.saveMeasurements}</span>
                </button>
              </div>
            </form>

          </div>
        </div>
      )}

    </div>
  );
};
