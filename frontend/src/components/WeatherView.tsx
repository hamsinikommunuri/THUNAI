import React from 'react';
import { 
  CloudSun, 
  Wind, 
  Droplets, 
  Clock, 
  AlertTriangle, 
  CheckCircle2, 
  Calendar, 
  ShieldCheck,
  Info
} from 'lucide-react';
import { WeatherData } from '../types';
import { translations, Language } from '../i18n/translations';

interface WeatherViewProps {
  weather: WeatherData | null;
  lang: Language;
}

export const WeatherView: React.FC<WeatherViewProps> = ({ weather, lang }) => {
  const t = translations[lang];

  if (!weather) {
    return (
      <div className="p-12 text-center text-mineral-muted">
        Loading real-time agro-meteorological forecasts...
      </div>
    );
  }

  const decision = weather.spray_safety.decision;
  const isOptimal = decision === 'SPRAY NOW';
  const isWait = decision === 'WAIT';

  return (
    <div className="space-y-8 animate-in fade-in duration-300 pb-12">
      
      {/* Header & Source Ribbon */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-white/10">
        <div>
          <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
            WEATHER INTELLIGENCE & SPRAY SAFETY
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Atmospheric & Spray Decision Gate ({weather.district})
          </h1>
        </div>
        <div className="text-right text-[11px] font-mono text-mineral-muted">
          <div>Source: Open-Meteo Global Agro Model</div>
          <div>Updated: {weather.updated_at}</div>
        </div>
      </div>

      {/* Spray Safety Monolith Card */}
      <div className={`p-6 sm:p-8 rounded-natural-lg border space-y-5 ${
        isOptimal ? 'bg-gradient-to-br from-[#143122] via-[#0E2419] to-carbon border-emerald/40 shadow-glow-emerald' :
        isWait ? 'bg-gradient-to-br from-[#2E1F0A] via-[#1A1205] to-carbon border-amber-500/40' :
        'bg-gradient-to-br from-[#2E0B0E] via-[#170507] to-carbon border-red-500/40'
      }`}>
        <div className="flex items-center justify-between">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-xs font-mono uppercase font-bold">
            <span className={`w-2 h-2 rounded-full ${isOptimal ? 'bg-emerald' : isWait ? 'bg-amber-400' : 'bg-red-400'} animate-ping`}></span>
            <span>DETERMINISTIC SPRAY EVALUATION</span>
          </div>
          <span className="text-xs font-mono text-mineral-muted">Statutory Agro-Meteorology</span>
        </div>

        <div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight flex items-center gap-3">
            {isOptimal && <CheckCircle2 className="w-8 h-8 text-emerald" />}
            {isWait && <AlertTriangle className="w-8 h-8 text-amber-400" />}
            <span>{decision}</span>
          </h2>
          <p className="text-sm sm:text-base text-mineral/90 mt-2 font-medium max-w-2xl">
            {weather.spray_safety.primary_reason}
          </p>
          <p className="text-xs sm:text-sm text-mineral-muted mt-1 leading-relaxed max-w-2xl">
            {weather.spray_safety.detailed_explanation}
          </p>
        </div>

        {/* Recommended Upcoming Spray Window */}
        <div className="p-4 rounded-2xl bg-black/40 border border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold block">
              RECOMMENDED APPLICATION WINDOW
            </span>
            <span className="text-base font-bold text-white">
              {weather.spray_safety.recommended_window}
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-mineral-muted">
            <Clock className="w-4 h-4 text-emerald" />
            <span>Optimal foliar adherence window</span>
          </div>
        </div>
      </div>

      {/* Atmospheric Variables Quad Barometer */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-[#0E1411] border border-white/10 space-y-2">
          <div className="flex items-center justify-between text-mineral-muted">
            <span className="text-xs font-medium">Temperature</span>
            <CloudSun className="w-4 h-4 text-sunlight" />
          </div>
          <div className="text-2xl font-bold text-white font-sans">
            {weather.current.temperature_c}°C
          </div>
          <p className="text-[11px] text-mineral-muted">
            {weather.current.temperature_c > 32 ? 'High heat: evaporation risk' : 'Optimal range for foliar spray'}
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-[#0E1411] border border-white/10 space-y-2">
          <div className="flex items-center justify-between text-mineral-muted">
            <span className="text-xs font-medium">Wind Speed</span>
            <Wind className="w-4 h-4 text-emerald" />
          </div>
          <div className="text-2xl font-bold text-white font-sans">
            {weather.current.wind_speed_kmh} <span className="text-xs font-normal">km/h</span>
          </div>
          <p className="text-[11px] text-mineral-muted">
            Gusts: {weather.current.wind_gust_kmh} km/h (Limit &lt; 15 km/h)
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-[#0E1411] border border-white/10 space-y-2">
          <div className="flex items-center justify-between text-mineral-muted">
            <span className="text-xs font-medium">Rain Probability</span>
            <Droplets className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white font-sans">
            {weather.current.precipitation_probability}%
          </div>
          <p className="text-[11px] text-mineral-muted">
            Active Rain: {weather.current.precipitation_mm} mm
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-[#0E1411] border border-white/10 space-y-2">
          <div className="flex items-center justify-between text-mineral-muted">
            <span className="text-xs font-medium">Humidity</span>
            <Droplets className="w-4 h-4 text-emerald" />
          </div>
          <div className="text-2xl font-bold text-white font-sans">
            {weather.current.humidity_percent}%
          </div>
          <p className="text-[11px] text-mineral-muted">
            Leaf cuticle drying rate: {weather.current.humidity_percent > 85 ? 'Slow' : 'Moderate'}
          </p>
        </div>
      </div>

      {/* Hourly Spray Safety Timeline (Next 24 Hours) */}
      <div className="p-6 rounded-natural-lg bg-[#0E1411] border border-white/10 space-y-4 shadow-natural">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
              HOURLY AGRO-METEOROLOGICAL FORECAST
            </span>
            <h3 className="text-lg font-bold text-white tracking-tight mt-0.5">
              24-Hour Spray Safety Timeline
            </h3>
          </div>
          <div className="flex items-center gap-3 text-xs font-mono">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald"></span> Safe</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Unsafe</span>
          </div>
        </div>

        <div className="overflow-x-auto no-scrollbar">
          <div className="flex items-center gap-2 min-w-max pb-2">
            {weather.hourly_forecast.map((h, i) => {
              const timeFormatted = h.time.split('T')[1] || h.time;
              return (
                <div
                  key={i}
                  className={`p-3 rounded-2xl border text-center w-24 shrink-0 transition-all ${
                    h.is_safe_for_spraying
                      ? 'bg-emerald/10 border-emerald/30 text-white'
                      : 'bg-carbon border-white/5 text-mineral-muted'
                  }`}
                >
                  <span className="text-xs font-mono font-bold block">{timeFormatted}</span>
                  <div className="my-1.5">
                    <span className="text-sm font-extrabold text-white block">{h.temperature_c}°</span>
                    <span className="text-[10px] text-blue-400 block font-mono">{h.precipitation_probability}% rain</span>
                  </div>
                  <div className="text-[10px] font-mono text-mineral-muted">
                    {h.wind_speed_kmh} km/h
                  </div>
                  <div className={`mt-2 py-0.5 text-[9px] font-mono uppercase font-bold rounded ${
                    h.is_safe_for_spraying ? 'bg-emerald text-obsidian' : 'bg-white/5 text-mineral-muted'
                  }`}>
                    {h.is_safe_for_spraying ? 'SAFE' : 'WAIT'}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* 7-Day Agricultural Outlook */}
      <div className="p-6 rounded-natural-lg bg-[#0E1411] border border-white/10 space-y-4 shadow-natural">
        <span className="text-[10px] font-mono tracking-widest text-emerald uppercase font-semibold">
          7-DAY REGIONAL OUTLOOK
        </span>
        <h3 className="text-lg font-bold text-white tracking-tight">
          Weekly Farm Weather Forecast
        </h3>

        <div className="space-y-2">
          {weather.daily_forecast.map((day, i) => (
            <div key={i} className="p-3.5 rounded-2xl bg-carbon/60 border border-white/5 flex items-center justify-between text-xs">
              <div className="flex items-center gap-3 w-32">
                <Calendar className="w-4 h-4 text-emerald" />
                <span className="font-semibold text-white">{day.date}</span>
              </div>
              <div className="text-mineral-muted truncate max-w-[150px]">
                {day.weather_condition}
              </div>
              <div className="flex items-center gap-3 text-right">
                <span className="font-mono text-white font-bold">{day.temp_max_c}° / {day.temp_min_c}°C</span>
                <span className="font-mono text-blue-400 w-16">{day.precipitation_probability_max}% rain</span>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
