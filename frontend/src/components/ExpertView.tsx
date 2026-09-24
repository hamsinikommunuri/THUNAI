import React, { useState } from 'react';
import { 
  ShieldAlert, 
  PhoneCall, 
  FileText, 
  Download, 
  Printer, 
  CheckCircle2, 
  ExternalLink,
  MapPin,
  Clock,
  Sparkles,
  Loader2
} from 'lucide-react';
import { LocationData, ExpertDossierResponse } from '../types';
import { translations, Language } from '../i18n/translations';
import { ThunaiApiClient } from '../api/client';

interface ExpertViewProps {
  location: LocationData | null;
  lang: Language;
}

export const ExpertView: React.FC<ExpertViewProps> = ({ location, lang }) => {
  const t = translations[lang];

  const [crop, setCrop] = useState('Tomato');
  const [district, setDistrict] = useState(location?.district || 'Coimbatore');
  const [farmerPhone, setFarmerPhone] = useState('');
  const [anomalyReason, setAnomalyReason] = useState('Observed unusual leaf spot progression with marginal chlorosis.');
  const [submitting, setSubmitting] = useState(false);
  const [dossier, setDossier] = useState<ExpertDossierResponse | null>(null);

  const handleGenerateDossier = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await ThunaiApiClient.requestSecondOpinion({
        crop,
        district: district || 'Coimbatore',
        reason: anomalyReason,
        farmer_phone: farmerPhone || undefined
      });
      setDossier(res);
    } catch (err) {
      console.error('Failed to generate dossier:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-white/10">
        <div>
          <span className="text-[10px] font-mono tracking-widest text-sunlight uppercase font-semibold">
            EXPERT ESCALATION & CASE DOSSIER
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Krishi Vigyan Kendra (KVK) Second Opinion
          </h1>
        </div>
        <div className="text-right text-[11px] font-mono text-mineral-muted">
          <div>Toll-Free Helpline: 1800-180-1551</div>
          <div>State Protocol: TNAU / ICAR Extension</div>
        </div>
      </div>

      {/* Overview Card */}
      <div className="p-6 rounded-natural-lg bg-gradient-to-r from-carbon via-[#181E15] to-carbon border border-white/10 space-y-3 shadow-natural">
        <div className="flex items-center gap-2 text-sunlight font-bold text-sm">
          <ShieldAlert className="w-5 h-5" />
          <span>Statutory Agricultural Escalation Protocol</span>
        </div>
        <p className="text-xs sm:text-sm text-mineral/80 leading-relaxed max-w-3xl">
          When field symptoms are ambiguous or visual confidence is borderline (&lt; 60%), THUNAI avoids speculative chemical advice. 
          Instead, we compile an official <strong>Agronomist Case Dossier</strong> containing your leaf scan, ambient weather variables, 
          and soil estimates for direct evaluation by certified extension scientists at your nearest Krishi Vigyan Kendra.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Dossier Generation Form */}
        <div className="p-6 rounded-natural-lg bg-[#0E1411] border border-white/10 space-y-4 shadow-natural">
          <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
            PREPARE ESCALATION DOSSIER
          </span>
          <h3 className="text-lg font-bold text-white tracking-tight">
            Case Details & Observed Anomaly
          </h3>

          <form onSubmit={handleGenerateDossier} className="space-y-3.5 pt-1">
            <div>
              <label className="text-[10px] font-mono text-mineral-muted uppercase block mb-1">Inspected Crop</label>
              <select
                value={crop}
                onChange={(e) => setCrop(e.target.value)}
                className="w-full p-2.5 rounded-xl bg-carbon border border-white/10 text-xs text-white focus:outline-none focus:border-emerald"
              >
                <option value="Tomato">Tomato (Solanum lycopersicum)</option>
                <option value="Potato">Potato (Solanum tuberosum)</option>
                <option value="Chilli">Chilli / Pepper (Capsicum annuum)</option>
                <option value="Rice">Rice / Paddy (Oryza sativa)</option>
                <option value="Banana">Banana (Musa paradisiaca)</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] font-mono text-mineral-muted uppercase block mb-1">Field District</label>
              <input
                type="text"
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                className="w-full p-2.5 rounded-xl bg-carbon border border-white/10 text-xs text-white focus:outline-none focus:border-emerald"
              />
            </div>

            <div>
              <label className="text-[10px] font-mono text-mineral-muted uppercase block mb-1">Farmer Contact Phone (Optional)</label>
              <input
                type="tel"
                placeholder="+91 98765 43210"
                value={farmerPhone}
                onChange={(e) => setFarmerPhone(e.target.value)}
                className="w-full p-2.5 rounded-xl bg-carbon border border-white/10 text-xs text-white placeholder-mineral-muted focus:outline-none focus:border-emerald"
              />
            </div>

            <div>
              <label className="text-[10px] font-mono text-mineral-muted uppercase block mb-1">Anomaly Description</label>
              <textarea
                rows={3}
                value={anomalyReason}
                onChange={(e) => setAnomalyReason(e.target.value)}
                className="w-full p-2.5 rounded-xl bg-carbon border border-white/10 text-xs text-white placeholder-mineral-muted focus:outline-none focus:border-emerald"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 rounded-xl bg-emerald hover:bg-emerald-bright text-obsidian font-bold text-xs flex items-center justify-center gap-2 transition-all shadow-md"
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
              <span>Generate Official Dossier</span>
            </button>
          </form>
        </div>

        {/* Dossier Output / Extension Center Info */}
        <div className="space-y-4">
          {dossier ? (
            <div className="p-6 rounded-natural-lg bg-[#0E1411] border-2 border-emerald/40 space-y-4 shadow-glow-emerald">
              <div className="flex items-center justify-between pb-3 border-b border-white/10">
                <div>
                  <span className="text-[10px] font-mono text-emerald uppercase font-bold">CASE DOSSIER READY</span>
                  <h4 className="text-xl font-extrabold text-white mt-0.5">#{dossier.dossier_id}</h4>
                </div>
                <span className="px-2.5 py-1 rounded-full bg-emerald/20 text-emerald text-[10px] font-mono font-bold uppercase">
                  {dossier.status}
                </span>
              </div>

              <div className="space-y-2 text-xs text-mineral">
                <p><strong>Assigned Center:</strong> {dossier.kvk_center.name}</p>
                <p><strong>Officer In Charge:</strong> {dossier.kvk_center.officer_in_charge}</p>
                <p><strong>Direct Extension Phone:</strong> {dossier.kvk_center.phone}</p>
                <p><strong>Official Address:</strong> {dossier.kvk_center.address}</p>
              </div>

              <div className="p-3.5 rounded-xl bg-carbon text-xs text-mineral-muted">
                {dossier.dispatch_message}
              </div>

              <div className="pt-2 flex items-center gap-3">
                <a
                  href={`tel:${dossier.kvk_center.phone}`}
                  className="px-4 py-2.5 rounded-xl bg-emerald text-obsidian font-bold text-xs flex items-center gap-2 shadow-sm"
                >
                  <PhoneCall className="w-3.5 h-3.5" />
                  <span>Call Officer Now</span>
                </a>
                <button
                  onClick={() => window.print()}
                  className="px-4 py-2.5 rounded-xl bg-white/10 text-white font-semibold text-xs flex items-center gap-2 hover:bg-white/15"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span>Print Case Dossier</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="p-6 rounded-natural-lg bg-[#0E1411] border border-white/10 space-y-4 shadow-natural">
              <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
                NATIONAL AGRICULTURAL HELPLINES
              </span>
              <h3 className="text-base font-bold text-white">
                Direct Agronomist Phone Numbers
              </h3>

              <div className="space-y-3 text-xs">
                <div className="p-3.5 rounded-xl bg-carbon border border-white/5 space-y-1">
                  <div className="flex items-center justify-between font-bold text-white">
                    <span>Kisan Call Center (KCC)</span>
                    <span className="text-emerald font-mono">1800-180-1551</span>
                  </div>
                  <p className="text-mineral-muted text-[11px]">
                    24x7 Toll-Free National Hotline · Available in 22 Regional Languages (Tamil, Hindi, Telugu, etc.)
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-carbon border border-white/5 space-y-1">
                  <div className="flex items-center justify-between font-bold text-white">
                    <span>TNAU Agritech Helpline</span>
                    <span className="text-emerald font-mono">1800-425-1660</span>
                  </div>
                  <p className="text-mineral-muted text-[11px]">
                    Tamil Nadu Agricultural University Extension Helpline · Monday to Friday 9:00 AM - 5:30 PM
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

      </div>

    </div>
  );
};
