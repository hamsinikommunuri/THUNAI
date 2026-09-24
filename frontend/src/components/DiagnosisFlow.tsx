import React, { useState, useRef } from 'react';
import { 
  Camera, 
  Upload, 
  RefreshCw, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldAlert, 
  Clock, 
  ExternalLink, 
  ChevronRight, 
  FileText, 
  Layers, 
  Eye, 
  Download,
  PhoneCall,
  Loader2,
  Check
} from 'lucide-react';
import { 
  DiagnosisResponse, 
  LocationData, 
  WeatherData, 
  ExpertDossierResponse 
} from '../types';
import { translations, Language } from '../i18n/translations';
import { ThunaiApiClient } from '../api/client';

interface DiagnosisFlowProps {
  initialCrop?: string;
  location: LocationData | null;
  weather: WeatherData | null;
  onDiagnosisComplete: (res: DiagnosisResponse) => void;
  lang: Language;
}

const SUPPORTED_CROPS = [
  { id: 'tomato', nameEn: 'Tomato', nameTa: 'தக்காளி', sci: 'Solanum lycopersicum', icon: '🍅' },
  { id: 'potato', nameEn: 'Potato', nameTa: 'உருளைக்கிழங்கு', sci: 'Solanum tuberosum', icon: '🥔' },
  { id: 'chilli', nameEn: 'Chilli / Pepper', nameTa: 'மிளகாய்', sci: 'Capsicum annuum', icon: '🌶️' },
  { id: 'paddy', nameEn: 'Paddy / Rice', nameTa: 'நெல்', sci: 'Oryza sativa', icon: '🌾' },
  { id: 'banana', nameEn: 'Banana', nameTa: 'வாழை', sci: 'Musa paradisiaca', icon: '🍌' },
];

export const DiagnosisFlow: React.FC<DiagnosisFlowProps> = ({
  initialCrop = 'tomato',
  location,
  weather,
  onDiagnosisComplete,
  lang,
}) => {
  const t = translations[lang];
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedCrop, setSelectedCrop] = useState<string>(initialCrop);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [diagnosisResult, setDiagnosisResult] = useState<DiagnosisResponse | null>(null);
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [showGradCam, setShowGradCam] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  
  // Second opinion escalation state
  const [escalating, setEscalating] = useState(false);
  const [dossierResult, setDossierResult] = useState<ExpertDossierResponse | null>(null);
  const [farmerPhone, setFarmerPhone] = useState('');
  const [escalationReason, setEscalationReason] = useState('Observed suspicious foliar lesion progression.');

  const handleFileChange = (file: File) => {
    setErrorMsg(null);
    if (!file.type.startsWith('image/')) {
      setErrorMsg('Please upload an image file (JPEG, PNG, WEBP).');
      return;
    }
    if (file.size > 15 * 1024 * 1024) {
      setErrorMsg('Image size exceeds 15MB limit.');
      return;
    }
    setSelectedImage(file);
    setImagePreviewUrl(URL.createObjectURL(file));
    setCurrentStep(2);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  // Quick 1-click test sample loader for rapid demonstration & verification
  const loadTestSample = async (cropId: string, sampleFilename: string, sampleLabel: string) => {
    setSelectedCrop(cropId);
    setErrorMsg(null);
    try {
      // Create synthetic sample or fetch from static samples
      const canvas = document.createElement('canvas');
      canvas.width = 224;
      canvas.height = 224;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.fillStyle = '#2E7D32';
        ctx.fillRect(0, 0, 224, 224);
        ctx.fillStyle = '#8D6E63';
        ctx.beginPath();
        ctx.arc(112, 112, 45, 0, 2 * Math.PI);
        ctx.fill();
      }
      canvas.toBlob(async (blob) => {
        if (blob) {
          const testFile = new File([blob], `${sampleFilename}.jpg`, { type: 'image/jpeg' });
          setSelectedImage(testFile);
          setImagePreviewUrl(canvas.toDataURL());
          setCurrentStep(2);
        }
      }, 'image/jpeg');
    } catch (err) {
      console.error('Failed to load sample:', err);
    }
  };

  const executeAnalysis = async () => {
    if (!selectedImage) return;
    setIsAnalyzing(true);
    setErrorMsg(null);
    setCurrentStep(3);

    try {
      const lat = location?.latitude || 11.0168;
      const lon = location?.longitude || 76.9558;
      const dist = location?.district || 'Coimbatore';

      const result = await ThunaiApiClient.diagnoseCrop(
        selectedImage,
        selectedCrop,
        dist,
        lat,
        lon
      );

      setDiagnosisResult(result);
      onDiagnosisComplete(result);
      setCurrentStep(4);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to complete diagnosis inference.');
      setCurrentStep(2);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const triggerEscalation = async () => {
    if (!diagnosisResult) return;
    setEscalating(true);
    try {
      const res = await ThunaiApiClient.requestSecondOpinion({
        crop: diagnosisResult.crop_display,
        district: location?.district || 'Coimbatore',
        diagnosis_id: diagnosisResult.diagnosis_id,
        reason: escalationReason,
        farmer_phone: farmerPhone || undefined
      });
      setDossierResult(res);
      setCurrentStep(9);
    } catch (err: any) {
      setErrorMsg(err.message || 'Escalation dispatch failed.');
    } finally {
      setEscalating(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-16">
      
      {/* 9-Step Walkthrough Progress Bar */}
      <div className="p-3 bg-[#0E1411] border border-white/10 rounded-2xl overflow-x-auto no-scrollbar shadow-natural">
        <div className="flex items-center gap-1 min-w-max">
          {[
            { num: 1, label: t.stepChooseCrop },
            { num: 2, label: t.stepUpload },
            { num: 3, label: t.stepAnalyze },
            { num: 4, label: t.stepDiagnosis },
            { num: 5, label: t.stepActions },
            { num: 6, label: t.stepDoseLock },
            { num: 7, label: t.stepWeatherCheck },
            { num: 8, label: t.stepEvidence },
            { num: 9, label: t.stepExpert },
          ].map((s) => (
            <button
              key={s.num}
              onClick={() => {
                if (diagnosisResult && s.num >= 4) setCurrentStep(s.num);
                else if (s.num <= 2) setCurrentStep(s.num);
              }}
              disabled={!diagnosisResult && s.num > 2}
              className={`px-3 py-1.5 rounded-xl text-xs font-mono transition-all flex items-center gap-1.5 ${
                currentStep === s.num
                  ? 'bg-emerald text-obsidian font-bold shadow-sm'
                  : currentStep > s.num
                  ? 'text-emerald-bright hover:bg-white/5'
                  : 'text-mineral-muted/50 cursor-not-allowed'
              }`}
            >
              <span>{s.num}.</span>
              <span className="font-sans text-[11px] font-medium">{s.label.split('. ')[1] || s.label}</span>
            </button>
          ))}
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-2xl bg-red-950/60 border border-red-500/40 text-red-200 text-xs flex items-center gap-3">
          <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* STEP 1: Crop Selection */}
      <div className="p-6 rounded-natural-lg bg-[#0E1411] border border-white/10 space-y-4 shadow-natural">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
              STEP 1 OF 9 · CROP ISOLATION
            </span>
            <h2 className="text-xl font-bold text-white tracking-tight mt-0.5">
              Which crop are you inspecting today?
            </h2>
          </div>
          <span className="text-xs font-mono text-emerald">
            {SUPPORTED_CROPS.find(c => c.id === selectedCrop)?.nameEn}
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
          {SUPPORTED_CROPS.map((c) => {
            const isSelected = selectedCrop === c.id;
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => setSelectedCrop(c.id)}
                className={`p-3.5 rounded-2xl border text-left transition-all ${
                  isSelected
                    ? 'bg-emerald/20 border-emerald shadow-glow-emerald text-white font-bold'
                    : 'bg-carbon/70 border-white/10 hover:border-emerald/40 text-mineral'
                }`}
              >
                <div className="text-2xl mb-1">{c.icon}</div>
                <div className="text-xs font-bold truncate">{lang === 'ta' ? c.nameTa : c.nameEn}</div>
                <div className="text-[10px] text-mineral-muted truncate font-serif italic">{c.sci}</div>
              </button>
            );
          })}
        </div>

        {/* Live Test Scenario Bar for Quick Evaluation */}
        <div className="pt-2 border-t border-white/5 flex flex-wrap items-center gap-2">
          <span className="text-[10px] font-mono text-emerald uppercase font-semibold">QUICK TEST SAMPLES:</span>
          {[
            { crop: 'tomato', file: 'tomato_early_blight', label: '🍅 Tomato Early Blight' },
            { crop: 'potato', file: 'potato_late_blight', label: '🥔 Potato Late Blight' },
            { crop: 'chilli', file: 'chilli_bacterial_spot', label: '🌶️ Chilli Spot' },
            { crop: 'rice', file: 'rice_bacterial_blight', label: '🌾 Rice Blight' },
            { crop: 'banana', file: 'banana_sigatoka', label: '🍌 Banana Sigatoka' },
          ].map((sample, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => loadTestSample(sample.crop, sample.file, sample.label)}
              className="px-2.5 py-1 rounded-xl bg-carbon hover:bg-emerald/20 border border-white/10 hover:border-emerald text-[11px] text-mineral transition-colors"
            >
              {sample.label}
            </button>
          ))}
        </div>
      </div>

      {/* STEP 2: Leaf Image Upload & Optical Preview */}
      <div className="p-6 rounded-natural-lg bg-[#0E1411] border border-white/10 space-y-5 shadow-natural">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
              STEP 2 OF 9 · FOLIAR CAPTURE
            </span>
            <h2 className="text-xl font-bold text-white tracking-tight mt-0.5">
              Upload leaf image or capture with camera
            </h2>
          </div>
          {selectedImage && (
            <button
              onClick={() => {
                setSelectedImage(null);
                setImagePreviewUrl(null);
                setDiagnosisResult(null);
                setCurrentStep(1);
              }}
              className="text-xs text-mineral-muted hover:text-white flex items-center gap-1"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>{t.retakeImage}</span>
            </button>
          )}
        </div>

        <input
          type="file"
          ref={fileInputRef}
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              handleFileChange(e.target.files[0]);
            }
          }}
        />

        {!imagePreviewUrl ? (
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className="cursor-pointer border-2 border-dashed border-emerald/40 hover:border-emerald rounded-natural-lg p-10 text-center space-y-4 bg-carbon/50 hover:bg-carbon transition-all group"
          >
            <div className="w-16 h-16 rounded-full bg-emerald/15 border border-emerald/30 flex items-center justify-center text-emerald mx-auto group-hover:scale-110 transition-transform shadow-glow-emerald">
              <Camera className="w-8 h-8" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-bold text-white">
                {t.uploadHint}
              </p>
              <p className="text-xs text-mineral-muted">
                {t.acceptedFormats}
              </p>
            </div>
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/[0.06] border border-white/10 text-xs font-semibold text-mineral">
              <Upload className="w-4 h-4 text-emerald" />
              <span>Choose Image File</span>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative w-full h-[360px] sm:h-[420px] rounded-3xl overflow-hidden border border-white/15 bg-black shadow-2xl flex items-center justify-center">
              <img
                src={showGradCam && diagnosisResult?.gradcam_image_base64 ? diagnosisResult.gradcam_image_base64 : imagePreviewUrl}
                alt="Selected crop leaf"
                className="w-full h-full object-contain"
              />

              {/* Optical Laser Scan Sweep Animation during active analysis */}
              {isAnalyzing && (
                <div className="animate-scan-line absolute left-0 right-0 h-[3px] bg-gradient-to-r from-transparent via-emerald-bright to-transparent shadow-[0_0_15px_#7CE8A1]"></div>
              )}

              {/* Heatmap overlay toggle badge */}
              {diagnosisResult?.gradcam_available && (
                <button
                  onClick={() => setShowGradCam(!showGradCam)}
                  className="absolute bottom-4 right-4 px-3.5 py-1.5 rounded-full bg-obsidian/85 backdrop-blur-md border border-white/15 text-xs font-mono font-semibold text-emerald-bright flex items-center gap-1.5 hover:bg-obsidian transition-colors shadow-lg"
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>{showGradCam ? 'Show Original' : 'Explain with Grad-CAM'}</span>
                </button>
              )}

              {/* Target Biological Isolation Chip */}
              <div className="absolute top-4 left-4 px-3 py-1.5 rounded-xl bg-obsidian/85 backdrop-blur-md border border-white/10 text-xs font-mono text-mineral flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald animate-pulse"></span>
                <span>Crop: {SUPPORTED_CROPS.find(c => c.id === selectedCrop)?.nameEn}</span>
              </div>
            </div>

            {/* Run Diagnosis CTA Button */}
            {!diagnosisResult && (
              <button
                onClick={executeAnalysis}
                disabled={isAnalyzing}
                className="w-full py-4 rounded-2xl bg-emerald hover:bg-emerald-bright text-obsidian font-extrabold text-sm flex items-center justify-center gap-2 shadow-lg shadow-emerald/30 transition-all transform hover:scale-[1.01]"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Analyzing Leaf Morphology (MobileNetV3 PyTorch)...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Run Deep Vision Diagnosis Now</span>
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </div>

      {/* STEP 4 & ONWARDS: Detailed Diagnostic Results */}
      {diagnosisResult && (
        <div className="space-y-6 animate-in fade-in duration-300">
          
          {/* Step 4: Diagnosis & Actual Model Confidence */}
          <div className="p-6 rounded-natural-lg bg-[#0E1411] border border-white/10 space-y-4 shadow-natural">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div>
                <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
                  STEP 4 · MODEL PREDICTION & CONFIDENCE
                </span>
                <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
                  {diagnosisResult.predicted_disease}
                </h2>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-sm text-mineral-muted font-serif italic">
                    {diagnosisResult.scientific_name}
                  </span>
                  <span className="text-white/20">·</span>
                  <span className="text-xs font-mono text-emerald">
                    {diagnosisResult.pathogen_type}
                  </span>
                </div>
              </div>

              {/* Heroic Real Confidence Metric */}
              <div className="text-right">
                <span className="text-[10px] font-mono text-mineral-muted uppercase block">Confidence</span>
                <div className="text-3xl sm:text-4xl font-extrabold text-emerald-bright font-sans">
                  {(diagnosisResult.confidence * 100).toFixed(1)}%
                </div>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full uppercase font-bold ${
                  diagnosisResult.confidence_tier === 'High' ? 'bg-emerald/20 text-emerald border border-emerald/40' :
                  diagnosisResult.confidence_tier === 'Moderate' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                  'bg-red-500/20 text-red-300 border border-red-500/40'
                }`}>
                  {diagnosisResult.confidence_tier} Confidence
                </span>
              </div>
            </div>

            {/* Top 3 Predictions Bar */}
            <div className="space-y-2 pt-1">
              <span className="text-[10px] font-mono text-mineral-muted uppercase tracking-wider block">
                Top Candidate Probabilities:
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                {diagnosisResult.top_predictions.map((cand, i) => (
                  <div key={i} className="p-2.5 rounded-xl bg-carbon border border-white/5 flex items-center justify-between text-xs">
                    <span className="text-mineral font-medium truncate max-w-[170px]">{cand.common_name}</span>
                    <span className="font-mono text-emerald font-bold">{cand.confidence_percent}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Low Confidence Warning Notice */}
            {diagnosisResult.confidence_tier === 'Low' && (
              <div className="p-4 rounded-2xl bg-amber-950/40 border border-amber-500/40 space-y-1">
                <div className="flex items-center gap-2 text-amber-400 font-bold text-xs">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Diagnosis Ambiguous (&lt; 60% Confidence)</span>
                </div>
                <p className="text-xs text-mineral/80 leading-relaxed">
                  The visual pattern displays overlap with other foliar diseases. Strong chemical sprays are restricted. 
                  Please upload another clear photo or request an agricultural expert second opinion below.
                </p>
              </div>
            )}
          </div>

          {/* Step 5: Action Narrative (Priority Actions & Controls) */}
          <div className="p-6 rounded-natural-lg bg-[#0E1411] border border-white/10 space-y-4 shadow-natural">
            <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
              STEP 5 · ACTION NARRATIVE
            </span>
            <h3 className="text-lg font-bold text-white tracking-tight">
              Immediate Cultural & Physical Interventions
            </h3>

            <div className="space-y-2.5">
              {diagnosisResult.immediate_actions.map((act, i) => (
                <div key={i} className="p-3.5 rounded-2xl bg-carbon/70 border border-white/5 flex items-start gap-3">
                  <span className="w-6 h-6 rounded-full bg-emerald/20 text-emerald-bright font-mono font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                    {i + 1}
                  </span>
                  <p className="text-xs text-mineral leading-relaxed font-medium">
                    {act}
                  </p>
                </div>
              ))}
            </div>

            {/* Biological Control Alternatives */}
            {diagnosisResult.biological_control && diagnosisResult.biological_control.length > 0 && (
              <div className="pt-2">
                <span className="text-[11px] font-mono text-emerald uppercase font-semibold block mb-1.5">
                  Biological & Organic Alternatives:
                </span>
                <div className="p-3.5 rounded-2xl bg-emerald/5 border border-emerald/20 text-xs text-mineral-muted space-y-1">
                  {diagnosisResult.biological_control.map((bio, idx) => (
                    <p key={idx}>🌿 {bio}</p>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Step 6: Dose Lock Ceremony (Statutory Pesticide Controls) */}
          <div className="relative p-6 sm:p-8 rounded-natural-lg bg-gradient-to-b from-carbon to-[#080B0A] border-2 border-emerald/40 space-y-5 shadow-[0_0_50px_-10px_rgba(95,203,135,0.2)]">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald/20 border border-emerald/40 text-emerald-bright text-xs font-mono font-bold uppercase">
                <Check className="w-4 h-4" />
                <span>{t.doseLockTitle}</span>
              </div>
              <span className="text-xs font-mono text-mineral-muted">Statutory Gate</span>
            </div>

            {diagnosisResult.dose_lock.is_available ? (
              <div className="text-center space-y-2 py-2">
                <span className="text-xs font-mono text-mineral-muted uppercase tracking-widest block">
                  {t.doseLockVerified}
                </span>
                <div className="flex items-baseline justify-center gap-2">
                  <span className="text-5xl sm:text-6xl font-extrabold text-white tracking-tight font-sans">
                    {diagnosisResult.dose_lock.dosage_per_liter?.split(' ')[0] || '2.0'}
                  </span>
                  <span className="text-2xl font-bold text-emerald">
                    {diagnosisResult.dose_lock.dosage_per_liter?.split(' ').slice(1).join(' ') || 'g / L'}
                  </span>
                </div>
                <h4 className="text-lg font-bold text-mineral mt-1">
                  {diagnosisResult.dose_lock.active_ingredient}
                </h4>
                <p className="text-xs text-mineral-muted">
                  Formulation: {diagnosisResult.dose_lock.formulation} · Dosage / Hectare: {diagnosisResult.dose_lock.dosage_per_hectare}
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg mx-auto pt-3 text-xs">
                  <div className="p-2.5 rounded-xl bg-carbon/80 border border-white/5">
                    <span className="text-[10px] font-mono text-mineral-muted block">Withholding Interval (PHI)</span>
                    <span className="font-bold text-emerald">{diagnosisResult.dose_lock.waiting_period_days} Days before harvest</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-carbon/80 border border-white/5">
                    <span className="text-[10px] font-mono text-mineral-muted block">Statutory Clearance</span>
                    <span className="font-bold text-emerald">{diagnosisResult.dose_lock.regulatory_status}</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-6 space-y-3">
                <div className="w-12 h-12 rounded-full bg-amber-500/20 text-amber-400 mx-auto flex items-center justify-center">
                  <ShieldAlert className="w-6 h-6" />
                </div>
                <h4 className="text-base font-bold text-white">
                  {diagnosisResult.dose_lock.status_text}
                </h4>
                <p className="text-xs text-mineral-muted max-w-md mx-auto">
                  {diagnosisResult.dose_lock.cautionary_notes || 'No chemical treatment is indicated or registered for this condition.'}
                </p>
              </div>
            )}

            <div className="p-3.5 rounded-xl bg-black/40 border border-white/5 text-[11px] text-mineral-muted leading-relaxed">
              <strong className="text-mineral font-semibold">Safety Covenant: </strong>
              {t.doseLockCovenant}
            </div>
          </div>

          {/* Step 7: Weather Shift Advisory */}
          <div className="p-6 rounded-natural-lg bg-[#0E1411] border border-white/10 space-y-4 shadow-natural">
            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
                STEP 7 · WEATHER SHIFT ADVISORY
              </span>
              <span className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded-full uppercase ${
                diagnosisResult.spray_safety.decision === 'SPRAY NOW' ? 'bg-emerald/20 text-emerald' : 'bg-amber-500/20 text-amber-300'
              }`}>
                {diagnosisResult.spray_safety.decision}
              </span>
            </div>

            <div className="space-y-2">
              <h4 className="text-base font-bold text-white">
                {diagnosisResult.spray_safety.primary_reason}
              </h4>
              <p className="text-xs text-mineral/80 leading-relaxed">
                {diagnosisResult.spray_safety.detailed_explanation}
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-carbon border border-emerald/30 flex items-center justify-between">
              <div>
                <span className="text-[10px] font-mono text-emerald uppercase font-semibold block">
                  Recommended Spraying Window:
                </span>
                <span className="text-sm font-bold text-white">
                  {diagnosisResult.spray_safety.recommended_window}
                </span>
              </div>
              <Clock className="w-5 h-5 text-emerald shrink-0" />
            </div>
          </div>

          {/* Step 8: Evidence Trace (Verifiable Reasoning Chain) */}
          <div className="p-6 rounded-natural-lg bg-[#0E1411] border border-white/10 space-y-4 shadow-natural">
            <div>
              <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
                STEP 8 · EVIDENCE TRACE
              </span>
              <h3 className="text-lg font-bold text-white tracking-tight mt-0.5">
                {t.evidenceTraceTitle}
              </h3>
              <p className="text-xs text-mineral-muted">
                Unbroken clinical provenance demonstrating the scientific backing for every step.
              </p>
            </div>

            <div className="relative pl-6 space-y-6 border-l-2 border-emerald/30 ml-3 py-2">
              {diagnosisResult.evidence_trace.map((step) => (
                <div key={step.step_number} className="relative group">
                  <span className="absolute -left-[31px] top-1 w-3.5 h-3.5 rounded-full bg-emerald border-2 border-charcoal"></span>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-bold">
                        {step.badge}
                      </span>
                      {step.source_url && (
                        <a
                          href={step.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-[10px] font-mono text-emerald hover:underline"
                        >
                          <span>View Source</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      )}
                    </div>
                    <h5 className="text-sm font-bold text-white">{step.title}</h5>
                    <p className="text-xs text-mineral-muted">{step.subtitle}</p>
                    <p className="text-xs text-mineral/80 leading-relaxed mt-1">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Step 9: Second Opinion / Expert Escalation CTA */}
          <div className="p-6 rounded-natural-lg bg-gradient-to-r from-carbon via-[#121B16] to-carbon border border-white/10 space-y-4 shadow-natural">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-mono tracking-widest text-sunlight uppercase font-semibold">
                  STEP 9 · SECOND OPINION
                </span>
                <h3 className="text-lg font-bold text-white tracking-tight mt-0.5">
                  Need Confirmation from an Agronomist?
                </h3>
              </div>
              <PhoneCall className="w-5 h-5 text-sunlight" />
            </div>

            <p className="text-xs text-mineral-muted leading-relaxed">
              {t.expertNotice}
            </p>

            {dossierResult ? (
              <div className="p-4 rounded-2xl bg-emerald/10 border border-emerald/40 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-emerald-bright">
                    Dossier #{dossierResult.dossier_id} Generated
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald/20 text-emerald uppercase font-bold">
                    Ready for Review
                  </span>
                </div>
                <div className="text-xs space-y-1 text-mineral">
                  <p><strong>Assigned Center:</strong> {dossierResult.kvk_center.name}</p>
                  <p><strong>Phone:</strong> {dossierResult.kvk_center.phone}</p>
                  <p><strong>Address:</strong> {dossierResult.kvk_center.address}</p>
                </div>
                <div className="flex items-center gap-2 pt-2">
                  <a
                    href={`tel:${dossierResult.kvk_center.phone}`}
                    className="px-4 py-2 rounded-xl bg-emerald text-obsidian font-bold text-xs flex items-center gap-1.5 shadow-sm"
                  >
                    <PhoneCall className="w-3.5 h-3.5" />
                    <span>Call Extension Center</span>
                  </a>
                  <button
                    onClick={() => window.print()}
                    className="px-4 py-2 rounded-xl bg-white/10 text-white font-semibold text-xs flex items-center gap-1.5 hover:bg-white/15"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Print Dossier</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <input
                    type="text"
                    placeholder="Your Phone Number (Optional)"
                    value={farmerPhone}
                    onChange={(e) => setFarmerPhone(e.target.value)}
                    className="p-3 rounded-xl bg-carbon border border-white/10 text-xs text-white placeholder-mineral-muted focus:outline-none focus:border-emerald"
                  />
                  <input
                    type="text"
                    placeholder="Notes or anomaly observed..."
                    value={escalationReason}
                    onChange={(e) => setEscalationReason(e.target.value)}
                    className="p-3 rounded-xl bg-carbon border border-white/10 text-xs text-white placeholder-mineral-muted focus:outline-none focus:border-emerald"
                  />
                </div>
                <button
                  onClick={triggerEscalation}
                  disabled={escalating}
                  className="px-6 py-3 rounded-xl bg-sunlight hover:bg-sunlight-warm text-obsidian font-bold text-xs flex items-center gap-2 transition-all shadow-md"
                >
                  {escalating ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                  <span>{t.dispatchDossier}</span>
                </button>
              </div>
            )}
          </div>

        </div>
      )}

    </div>
  );
};
