import React from 'react';
import { 
  CloudRain, 
  Wind, 
  Droplets, 
  Clock, 
  PhoneCall, 
  ShieldCheck, 
  ArrowRight,
  AlertTriangle,
  CheckCircle2
} from 'lucide-react';
import { WeatherData } from '../types';
import { translations, Language } from '../i18n/translations';

interface RightPanelProps {
  weather: WeatherData | null;
  onNavigateToScanner: () => void;
  onNavigateToWeather: () => void;
  onNavigateToExpert: () => void;
  lang: Language;
}

export const RightPanel: React.FC<RightPanelProps> = ({
  weather,
  onNavigateToScanner,
  onNavigateToWeather,
  onNavigateToExpert,
  lang,
}) => {
  const t = translations[lang];

  if (!weather) {
    return (
      <aside className="w-80 shrink-0 hidden xl:flex flex-col p-6 bg-[#0A0E0C] border-l border-white/[0.08]">
        <div className="animate-pulse space-y-4">
          <div className="h-28 bg-carbon rounded-2xl"></div>
          <div className="h-40 bg-carbon rounded-2xl"></div>
        </div>
      </aside>
    );
  }

  const decision = weather.spray_safety.decision;
  const isOptimal = decision === 'SPRAY NOW';
  const isWait = decision === 'WAIT';

  return (
    <aside className="w-80 shrink-0 hidden xl:flex flex-col justify-between p-6 bg-[#0A0E0C] border-l border-white/[0.08] min-h-[calc(100vh-65px)]">
      <div className="space-y-5">
        
        {/* Spray Safety Atmospheric Status Card */}
        <div className={`relative p-5 rounded-natural-lg border transition-all ${
          isOptimal ? 'bg-gradient-to-b from-[#143122] to-[#0A1410] border-emerald/40 shadow-glow-emerald' :
          isWait ? 'bg-gradient-to-b from-[#2A1D0B] to-[#120D05] border-amber-500/40 shadow-[0_0_25px_-5px_rgba(245,158,11,0.25)]' :
          'bg-gradient-to-b from-[#2E0F12] to-[#140608] border-red-500/40'
        }`}>
          <div className="flex items-center justify-between pb-2">
            <div className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full animate-ping ${
                isOptimal ? 'bg-emerald' : isWait ? 'bg-amber-400' : 'bg-red-400'
              }`}></span>
              <span className={`text-[10px] font-mono tracking-widest uppercase font-bold ${
                isOptimal ? 'text-emerald-bright' : isWait ? 'text-amber-400' : 'text-red-400'
              }`}>
                WEATHER SHIFT
              </span>
            </div>
            <span className="text-[10px] font-mono text-mineral-muted">Live Gate</span>
          </div>

          <div className="my-2">
            <h3 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
              {isOptimal && <CheckCircle2 className="w-5 h-5 text-emerald" />}
              {isWait && <AlertTriangle className="w-5 h-5 text-amber-400" />}
              <span>{decision}</span>
            </h3>
            <p className="text-xs text-mineral/80 mt-1 leading-snug">
              {weather.spray_safety.primary_reason}
            </p>
          </div>

          {/* Quick Metrics Barometer */}
          <div className="grid grid-cols-3 gap-1.5 pt-3 border-t border-white/10 text-center">
            <div className="p-2 rounded-xl bg-carbon/60">
              <span className="text-[9px] font-mono text-mineral-muted uppercase block">Precip</span>
              <span className="text-xs font-bold text-white">{weather.current.precipitation_probability}%</span>
            </div>
            <div className="p-2 rounded-xl bg-carbon/60">
              <span className="text-[9px] font-mono text-mineral-muted uppercase block">Wind</span>
              <span className="text-xs font-bold text-white">{weather.current.wind_speed_kmh} <span className="text-[9px]">km/h</span></span>
            </div>
            <div className="p-2 rounded-xl bg-carbon/60">
              <span className="text-[9px] font-mono text-mineral-muted uppercase block">Humidity</span>
              <span className="text-xs font-bold text-white">{weather.current.humidity_percent}%</span>
            </div>
          </div>
        </div>

        {/* Recommended Spray Window Card */}
        <div 
          onClick={onNavigateToWeather}
          className="cursor-pointer p-4 rounded-2xl bg-carbon/80 hover:bg-carbon border border-white/10 hover:border-emerald/30 transition-all space-y-2 group"
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold flex items-center gap-1.5">
              <Clock className="w-3 h-3" />
              <span>RECOMMENDED WINDOW</span>
            </span>
            <ArrowRight className="w-3.5 h-3.5 text-mineral-muted group-hover:text-emerald group-hover:translate-x-0.5 transition-transform" />
          </div>
          <p className="text-xs font-semibold text-white leading-snug">
            {weather.spray_safety.recommended_window}
          </p>
          <p className="text-[11px] text-mineral-muted">
            Tap to view 24-hour hourly spray safety curve.
          </p>
        </div>

        {/* 1-Tap Crop Diagnostic Trigger */}
        <div 
          onClick={onNavigateToScanner}
          className="cursor-pointer p-4 rounded-2xl bg-gradient-to-r from-emerald/15 to-transparent border border-emerald/30 hover:border-emerald transition-all space-y-2"
        >
          <div className="flex items-center gap-2 text-emerald">
            <ShieldCheck className="w-4 h-4" />
            <span className="text-xs font-bold">Diagnose Crop Anomaly</span>
          </div>
          <p className="text-[11px] text-mineral-muted leading-relaxed">
            Upload tomato, potato, chilli, rice or banana leaf for deep vision classification.
          </p>
        </div>

        {/* KVK Extension Helplines Card */}
        <div 
          onClick={onNavigateToExpert}
          className="cursor-pointer p-4 rounded-2xl bg-carbon/80 hover:bg-carbon border border-white/10 transition-all space-y-2.5"
        >
          <div className="flex items-center gap-2 text-sunlight">
            <PhoneCall className="w-4 h-4" />
            <span className="text-xs font-bold">KVK Extension Helpdesk</span>
          </div>
          <p className="text-[11px] text-mineral-muted leading-relaxed">
            Need an agronomist second opinion? THUNAI directly maps your local Krishi Vigyan Kendra.
          </p>
          <div className="text-[10px] font-mono text-emerald font-semibold">
            Toll-Free Helpline: 1800-180-1551
          </div>
        </div>

      </div>

      {/* Attribution & Timestamp */}
      <div className="pt-3 border-t border-white/[0.06] text-[10px] font-mono text-mineral-muted/60 space-y-0.5">
        <div>Weather: Open-Meteo Global Blended Model</div>
        <div>Updated: {weather.updated_at}</div>
      </div>
    </aside>
  );
};
