import React from 'react';
import { 
  Sprout, 
  MapPin, 
  CloudSun, 
  Layers, 
  ShieldCheck, 
  ArrowRight, 
  Sparkles, 
  Clock, 
  CheckCircle,
  AlertTriangle,
  Droplets,
  Wind,
  Thermometer,
  Compass
} from 'lucide-react';
import { 
  LocationData, 
  WeatherData, 
  SoilProfile, 
  CropRecommendationData, 
  HistoryItem 
} from '../types';
import { translations, Language } from '../i18n/translations';

interface DashboardViewProps {
  location: LocationData | null;
  weather: WeatherData | null;
  soil: SoilProfile | null;
  cropRecs: CropRecommendationData | null;
  history: HistoryItem[];
  onNavigateToTab: (tab: string) => void;
  onSelectCropForDiagnosis: (cropId: string) => void;
  lang: Language;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  location,
  weather,
  soil,
  cropRecs,
  history,
  onNavigateToTab,
  onSelectCropForDiagnosis,
  lang,
}) => {
  const t = translations[lang];

  return (
    <div className="space-y-8 animate-in fade-in duration-300 pb-12">
      
      {/* Hero Section with Botanical Atmosphere */}
      <div className="relative overflow-hidden rounded-natural-lg border border-white/10 p-6 sm:p-10 bg-gradient-to-br from-[#0F2417] via-[#0A1610] to-[#080B0A] shadow-natural-lg">
        {/* Ambient atmospheric gradients */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald/10 blur-[100px] pointer-events-none rounded-full"></div>
        <div className="absolute bottom-0 left-1/3 w-80 h-80 bg-sunlight/10 blur-[120px] pointer-events-none rounded-full"></div>

        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald/15 border border-emerald/30 text-emerald-bright text-xs font-mono font-semibold uppercase">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI FIELD INTELLIGENCE</span>
          </div>
          
          <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight leading-[1.1] font-sans">
            {t.heroTitle}
          </h1>
          
          <p className="text-sm sm:text-base text-mineral/80 font-normal leading-relaxed">
            {t.heroSubtitle}
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              onClick={() => onNavigateToTab('vision')}
              className="px-6 py-3.5 rounded-2xl bg-emerald hover:bg-emerald-bright text-obsidian font-bold text-sm flex items-center gap-2 shadow-lg shadow-emerald/25 transition-all transform hover:-translate-y-0.5"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>{t.runDiagnosis}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => onNavigateToTab('weather')}
              className="px-5 py-3.5 rounded-2xl bg-white/[0.06] hover:bg-white/[0.1] border border-white/10 text-white font-semibold text-sm transition-all"
            >
              {t.navWeather}
            </button>
          </div>
        </div>
      </div>

      {/* Location Provenance Banner */}
      {location && (
        <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-2xl bg-carbon/70 border border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-emerald/15 flex items-center justify-center text-emerald">
              <MapPin className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-bold">
                  {t.detectedLocation}
                </span>
                <span className="text-[9px] px-1.5 py-0.2 rounded bg-white/10 text-mineral-muted font-mono">
                  GPS Active
                </span>
              </div>
              <p className="text-sm font-bold text-white">
                {location.display_name}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs font-mono text-mineral-muted">
            <span>Lat: {location.latitude.toFixed(4)}°, Lon: {location.longitude.toFixed(4)}°</span>
            <span className="hidden sm:inline text-white/20">|</span>
            <span className="hidden sm:inline">Source: {location.source}</span>
          </div>
        </div>
      )}

      {/* Triple Pillar Grid: Weather, Soil, Cropping Season */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        
        {/* 1. Live Weather Glance */}
        <div 
          onClick={() => onNavigateToTab('weather')}
          className="cursor-pointer group p-6 rounded-natural bg-[#0E1411] border border-white/10 hover:border-emerald/40 transition-all space-y-4 shadow-natural"
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold flex items-center gap-1.5">
              <CloudSun className="w-3.5 h-3.5" />
              <span>LIVE WEATHER</span>
            </span>
            <ArrowRight className="w-4 h-4 text-mineral-muted group-hover:text-emerald group-hover:translate-x-1 transition-all" />
          </div>

          {weather ? (
            <>
              <div className="flex items-baseline justify-between">
                <div>
                  <span className="text-4xl font-extrabold text-white tracking-tight">
                    {weather.current.temperature_c}°
                  </span>
                  <span className="text-xs text-mineral-muted ml-1 font-medium">C</span>
                </div>
                <span className={`text-xs font-mono px-2.5 py-1 rounded-full font-bold uppercase ${
                  weather.spray_safety.decision === 'SPRAY NOW' ? 'bg-emerald/20 text-emerald border border-emerald/40' :
                  weather.spray_safety.decision === 'WAIT' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                  'bg-red-500/20 text-red-300 border border-red-500/40'
                }`}>
                  {weather.spray_safety.decision}
                </span>
              </div>

              <p className="text-xs text-mineral font-medium">
                {weather.current.weather_condition} · Wind: {weather.current.wind_speed_kmh} km/h
              </p>

              <div className="pt-2 border-t border-white/5 flex items-center justify-between text-[11px] text-mineral-muted">
                <span>Rain Chance: {weather.current.precipitation_probability}%</span>
                <span>Humidity: {weather.current.humidity_percent}%</span>
              </div>
            </>
          ) : (
            <div className="h-24 flex items-center justify-center text-xs text-mineral-muted">Loading weather...</div>
          )}
        </div>

        {/* 2. Regional Soil Glance */}
        <div 
          onClick={() => onNavigateToTab('soil')}
          className="cursor-pointer group p-6 rounded-natural bg-[#0E1411] border border-white/10 hover:border-emerald/40 transition-all space-y-4 shadow-natural"
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5" />
              <span>SOIL INTELLIGENCE</span>
            </span>
            <ArrowRight className="w-4 h-4 text-mineral-muted group-hover:text-emerald group-hover:translate-x-1 transition-all" />
          </div>

          {soil ? (
            <>
              <div>
                <p className="text-xs text-mineral-muted font-mono uppercase">{soil.district} Tract</p>
                <h3 className="text-base font-bold text-white truncate mt-0.5">
                  {soil.dominant_soil_type}
                </h3>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 rounded-xl bg-carbon">
                  <span className="text-[9px] font-mono text-mineral-muted block uppercase">pH Bracket</span>
                  <span className="font-semibold text-emerald">{soil.ph_range}</span>
                </div>
                <div className="p-2 rounded-xl bg-carbon">
                  <span className="text-[9px] font-mono text-mineral-muted block uppercase">Organic Carbon</span>
                  <span className="font-semibold text-white">{soil.organic_carbon}</span>
                </div>
              </div>

              <div className="pt-2 border-t border-white/5 text-[10px] text-mineral-muted truncate">
                {soil.warning_notice}
              </div>
            </>
          ) : (
            <div className="h-24 flex items-center justify-center text-xs text-mineral-muted">Loading soil profile...</div>
          )}
        </div>

        {/* 3. Cropping Season & Suitability Engine */}
        <div 
          onClick={() => onNavigateToTab('planner')}
          className="cursor-pointer group p-6 rounded-natural bg-[#0E1411] border border-white/10 hover:border-emerald/40 transition-all space-y-4 shadow-natural"
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold flex items-center gap-1.5">
              <Compass className="w-3.5 h-3.5" />
              <span>SEASON & SUITABILITY</span>
            </span>
            <ArrowRight className="w-4 h-4 text-mineral-muted group-hover:text-emerald group-hover:translate-x-1 transition-all" />
          </div>

          {cropRecs ? (
            <>
              <div>
                <p className="text-[10px] font-mono text-mineral-muted uppercase">Agro-Climatic Window</p>
                <h3 className="text-base font-bold text-emerald-bright mt-0.5">
                  {cropRecs.current_season}
                </h3>
              </div>

              <p className="text-xs text-mineral/80 leading-snug">
                Top suitable regional crops:
              </p>

              <div className="flex flex-wrap gap-1.5 pt-1">
                {cropRecs.recommended_crops.slice(0, 3).map((c) => (
                  <span key={c.crop_id} className="px-2.5 py-1 rounded-full bg-emerald/15 border border-emerald/30 text-emerald-bright text-xs font-semibold">
                    {c.name_en} ({c.suitability})
                  </span>
                ))}
              </div>
            </>
          ) : (
            <div className="h-24 flex items-center justify-center text-xs text-mineral-muted">Evaluating agronomic season...</div>
          )}
        </div>

      </div>

      {/* Recommended Crops Interactive Carousel */}
      {cropRecs && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
                AGRONOMIC CROP SUITABILITY
              </span>
              <h2 className="text-xl font-bold text-white tracking-tight mt-0.5">
                Recommended Crops for {cropRecs.location}
              </h2>
            </div>
            <button
              onClick={() => onNavigateToTab('planner')}
              className="text-xs text-emerald hover:underline font-semibold flex items-center gap-1"
            >
              <span>View Full Evaluation</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {cropRecs.recommended_crops.slice(0, 3).map((crop) => (
              <div
                key={crop.crop_id}
                className="p-5 rounded-2xl bg-carbon/70 border border-white/10 hover:border-emerald/40 transition-all flex flex-col justify-between space-y-3"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-base font-bold text-white">{crop.name_en}</h3>
                      <p className="text-xs text-mineral-muted font-serif italic">{crop.scientific_name}</p>
                    </div>
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase font-mono ${
                      crop.suitability === 'High' ? 'bg-emerald/20 text-emerald border border-emerald/30' :
                      'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    }`}>
                      {crop.suitability}
                    </span>
                  </div>

                  <ul className="mt-3 space-y-1.5 text-xs text-mineral-muted">
                    {crop.reasons.slice(0, 2).map((r, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <CheckCircle className="w-3.5 h-3.5 text-emerald shrink-0 mt-0.5" />
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <button
                  onClick={() => {
                    onSelectCropForDiagnosis(crop.crop_id);
                    onNavigateToTab('vision');
                  }}
                  className="w-full py-2 rounded-xl bg-white/[0.05] hover:bg-emerald hover:text-obsidian text-xs font-semibold text-white transition-all flex items-center justify-center gap-1.5"
                >
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Diagnose This Crop</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Launch Diagnosis Bar */}
      <div className="p-6 sm:p-8 rounded-natural-lg bg-gradient-to-r from-emerald/20 via-forest/40 to-carbon border border-emerald/30 flex flex-col sm:flex-row items-center justify-between gap-5">
        <div className="space-y-1 text-center sm:text-left">
          <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-bold">
            MOBILE VISION DIAGNOSIS
          </span>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            See foliar spots or yellowing on your crop?
          </h2>
          <p className="text-xs sm:text-sm text-mineral-muted">
            Upload leaf photo. THUNAI gives verified disease diagnosis, Dose Lock safety, and spray advisories.
          </p>
        </div>

        <button
          onClick={() => onNavigateToTab('vision')}
          className="shrink-0 px-6 py-3.5 rounded-2xl bg-emerald hover:bg-emerald-bright text-obsidian font-bold text-sm flex items-center gap-2 shadow-lg shadow-emerald/30 transition-all transform hover:scale-105"
        >
          <ShieldCheck className="w-5 h-5" />
          <span>Launch Vision Scanner</span>
        </button>
      </div>

      {/* Recent Farm Diagnoses */}
      {history.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white">Recent Field Scans</h2>
            <button
              onClick={() => onNavigateToTab('history')}
              className="text-xs text-emerald hover:underline font-semibold"
            >
              View All History
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {history.slice(0, 3).map((item) => (
              <div key={item.id} className="p-4 rounded-2xl bg-carbon/60 border border-white/5 flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-forest-deep flex items-center justify-center text-emerald shrink-0 overflow-hidden">
                  {item.image_url ? (
                    <img src={item.image_url} alt={item.disease_name} className="w-full h-full object-cover" />
                  ) : (
                    <Sprout className="w-6 h-6" />
                  )}
                </div>
                <div className="overflow-hidden">
                  <span className="text-[10px] font-mono text-emerald uppercase font-bold">{item.crop}</span>
                  <h4 className="text-xs font-bold text-white truncate">{item.disease_name}</h4>
                  <p className="text-[10px] text-mineral-muted">{item.created_at} · Confidence: {Math.round(item.confidence * 100)}%</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
};
