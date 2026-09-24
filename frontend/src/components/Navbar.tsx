import React, { useState } from 'react';
import { 
  Sprout, 
  MapPin, 
  CloudSun, 
  Globe, 
  Menu, 
  X, 
  Search, 
  Check, 
  Navigation,
  Loader2
} from 'lucide-react';
import { LocationData, WeatherData } from '../types';
import { translations, Language } from '../i18n/translations';
import { ThunaiApiClient } from '../api/client';

interface NavbarProps {
  location: LocationData | null;
  weather: WeatherData | null;
  lang: Language;
  onLanguageChange: (lang: Language) => void;
  onLocationUpdate: (loc: LocationData) => void;
  onRefreshLocation: () => void;
  isLocating: boolean;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  location,
  weather,
  lang,
  onLanguageChange,
  onLocationUpdate,
  onRefreshLocation,
  isLocating,
  activeTab,
  onTabChange,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [locationModalOpen, setLocationModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const t = translations[lang];

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    try {
      const results = await ThunaiApiClient.searchLocations(searchQuery);
      setSearchResults(results);
    } catch (err) {
      console.error('Location search failed:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const selectSearchResult = async (item: any) => {
    try {
      const loc = await ThunaiApiClient.reverseGeocode(item.latitude, item.longitude);
      onLocationUpdate(loc);
      setLocationModalOpen(false);
      setSearchQuery('');
      setSearchResults([]);
    } catch {
      onLocationUpdate({
        latitude: item.latitude,
        longitude: item.longitude,
        village_or_town: item.district,
        district: item.district,
        state: item.state,
        country: item.country,
        display_name: item.display_name,
        source: 'Manual District Search',
        timestamp: new Date().toLocaleTimeString()
      });
      setLocationModalOpen(false);
    }
  };

  return (
    <>
      <header className="sticky top-0 z-50 bg-[#0E1411]/90 backdrop-blur-xl border-b border-white/[0.08] px-4 lg:px-8 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          
          {/* Logo & Platform Name */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => onTabChange('dashboard')}>
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-emerald to-nature-800 flex items-center justify-center shadow-glow-emerald border border-emerald/40">
              <Sprout className="w-6 h-6 text-obsidian" strokeWidth={2.5} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-tight text-white font-sans">THUNAI</span>
                <span className="text-[10px] uppercase font-mono tracking-widest px-2 py-0.5 rounded-full bg-emerald/20 text-emerald-bright border border-emerald/30 font-semibold">
                  v2.0 AI
                </span>
              </div>
              <p className="text-[11px] text-mineral-muted hidden sm:block">
                {t.appTagline}
              </p>
            </div>
          </div>

          {/* Center Pill: Location & Weather Sensor Ribbon */}
          <div className="hidden md:flex items-center gap-3">
            {/* Location Indicator Button */}
            <button
              onClick={() => setLocationModalOpen(true)}
              className="group flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-carbon/80 hover:bg-carbon border border-white/10 hover:border-emerald/40 transition-all text-xs font-medium text-mineral"
            >
              <MapPin className="w-3.5 h-3.5 text-emerald group-hover:scale-110 transition-transform" />
              <span className="max-w-[140px] truncate">
                {location ? `${location.district}, ${location.state}` : t.detectingLocation}
              </span>
              <span className="text-[10px] text-mineral-muted underline group-hover:text-emerald">Edit</span>
            </button>

            {/* Weather Sensor Pill */}
            {weather && (
              <div 
                onClick={() => onTabChange('weather')}
                className="flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-carbon/80 border border-white/10 text-xs font-medium text-mineral cursor-pointer hover:border-sunlight/40 transition-all"
              >
                <CloudSun className="w-4 h-4 text-sunlight animate-pulse" />
                <span className="font-semibold text-white">{weather.current.temperature_c}°C</span>
                <span className="text-white/20">·</span>
                <span className="text-mineral-muted truncate max-w-[110px]">{weather.current.weather_condition}</span>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full uppercase font-bold ${
                  weather.spray_safety.decision === 'SPRAY NOW' ? 'bg-emerald/20 text-emerald border border-emerald/40' :
                  weather.spray_safety.decision === 'WAIT' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                  'bg-red-500/20 text-red-300 border border-red-500/40'
                }`}>
                  {weather.spray_safety.decision}
                </span>
              </div>
            )}
          </div>

          {/* Right: Language Toggle & Mobile Drawer */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Language Selector */}
            <div className="flex items-center bg-carbon rounded-full p-1 border border-white/10">
              <button
                onClick={() => onLanguageChange('en')}
                className={`px-2.5 py-1 rounded-full text-xs font-medium transition-all ${
                  lang === 'en' ? 'bg-emerald text-obsidian font-bold shadow-sm' : 'text-mineral-muted hover:text-white'
                }`}
              >
                EN
              </button>
              <button
                onClick={() => onLanguageChange('ta')}
                className={`px-2.5 py-1 rounded-full text-xs font-medium transition-all ${
                  lang === 'ta' ? 'bg-emerald text-obsidian font-bold shadow-sm' : 'text-mineral-muted hover:text-white'
                }`}
              >
                தமிழ்
              </button>
            </div>

            {/* Mobile Hamburger Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-xl bg-carbon border border-white/10 text-mineral hover:text-white"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden mt-3 pt-3 border-t border-white/10 space-y-2 animate-in slide-in-from-top-2 duration-200">
            {/* Mobile Location / Weather Strip */}
            <div className="flex items-center justify-between px-2 py-2 bg-carbon rounded-xl border border-white/5 text-xs">
              <button 
                onClick={() => { setLocationModalOpen(true); setMobileMenuOpen(false); }}
                className="flex items-center gap-1.5 text-emerald font-medium"
              >
                <MapPin className="w-3.5 h-3.5" />
                <span>{location?.district || 'Select Location'}</span>
              </button>
              {weather && (
                <div className="flex items-center gap-1.5 text-mineral font-medium">
                  <CloudSun className="w-3.5 h-3.5 text-sunlight" />
                  <span>{weather.current.temperature_c}°C</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald/20 text-emerald">
                    {weather.spray_safety.decision}
                  </span>
                </div>
              )}
            </div>

            {/* Navigation Links */}
            <div className="grid grid-cols-2 gap-2 pt-1">
              {[
                { id: 'dashboard', label: t.navDashboard },
                { id: 'vision', label: t.navVision },
                { id: 'weather', label: t.navWeather },
                { id: 'soil', label: t.navSoil },
                { id: 'planner', label: t.navPlanner },
                { id: 'history', label: t.navHistory },
                { id: 'expert', label: t.navExpert },
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    onTabChange(item.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`px-3 py-2.5 rounded-xl text-xs text-left font-medium transition-all ${
                    activeTab === item.id 
                      ? 'bg-emerald text-obsidian font-bold shadow-md' 
                      : 'bg-carbon text-mineral hover:bg-carbon/80'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </header>

      {/* Manual Location Search & GPS Modal */}
      {locationModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian/80 backdrop-blur-md animate-in fade-in duration-150">
          <div className="relative w-full max-w-md bg-[#0F1411] border border-white/10 rounded-natural-lg p-6 shadow-natural-dark space-y-4">
            
            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <div className="flex items-center gap-2">
                <MapPin className="w-5 h-5 text-emerald" />
                <h3 className="text-base font-bold text-white">Select Agricultural Location</h3>
              </div>
              <button 
                onClick={() => setLocationModalOpen(false)}
                className="w-8 h-8 rounded-full bg-carbon hover:bg-white/10 flex items-center justify-center text-mineral"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* 1-Tap Browser GPS Permission Trigger */}
            <button
              onClick={() => {
                onRefreshLocation();
                setLocationModalOpen(false);
              }}
              disabled={isLocating}
              className="w-full py-3 px-4 rounded-2xl bg-emerald/15 hover:bg-emerald/25 border border-emerald/40 text-emerald-bright text-xs font-semibold flex items-center justify-center gap-2 transition-all"
            >
              {isLocating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Navigation className="w-4 h-4" />}
              <span>{t.allowLocation} (GPS Auto-Detect)</span>
            </button>

            <div className="flex items-center gap-3">
              <div className="flex-1 h-px bg-white/10"></div>
              <span className="text-[10px] uppercase font-mono text-mineral-muted tracking-widest">Or Search District</span>
              <div className="flex-1 h-px bg-white/10"></div>
            </div>

            {/* Search Input */}
            <form onSubmit={handleSearch} className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={t.manualLocationSearch}
                className="w-full py-2.5 pl-10 pr-20 rounded-2xl bg-carbon border border-white/15 text-xs text-white placeholder-mineral-muted focus:outline-none focus:border-emerald"
              />
              <Search className="w-4 h-4 text-mineral-muted absolute left-3.5 top-3" />
              <button
                type="submit"
                disabled={isSearching}
                className="absolute right-1.5 top-1.5 px-3 py-1.5 bg-emerald text-obsidian rounded-xl text-xs font-semibold hover:bg-emerald-bright transition-colors"
              >
                {isSearching ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Search'}
              </button>
            </form>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="max-h-48 overflow-y-auto space-y-1.5 pt-1 pr-1">
                {searchResults.map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => selectSearchResult(item)}
                    className="w-full p-2.5 rounded-xl bg-carbon/60 hover:bg-carbon border border-white/5 hover:border-emerald/30 text-left text-xs flex items-center justify-between group transition-all"
                  >
                    <div>
                      <p className="font-semibold text-mineral group-hover:text-emerald">{item.district}</p>
                      <p className="text-[11px] text-mineral-muted truncate max-w-[280px]">{item.display_name}</p>
                    </div>
                    <Check className="w-4 h-4 text-emerald opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
            )}

            {/* Quick District Presets */}
            <div className="space-y-1 pt-2">
              <span className="text-[10px] font-mono text-mineral-muted uppercase tracking-wider block">Major Agricultural Belts:</span>
              <div className="flex flex-wrap gap-1.5">
                {[
                  { name: 'Coimbatore', lat: 11.0168, lon: 76.9558 },
                  { name: 'Thanjavur', lat: 10.7870, lon: 79.1378 },
                  { name: 'Salem', lat: 11.6643, lon: 78.1460 },
                  { name: 'Guntur', lat: 16.3067, lon: 80.4365 },
                  { name: 'Shimoga', lat: 13.9299, lon: 75.5681 },
                  { name: 'Pune', lat: 18.5204, lon: 73.8567 },
                ].map((d) => (
                  <button
                    key={d.name}
                    onClick={() => selectSearchResult({ district: d.name, state: 'India', country: 'India', display_name: `${d.name} Agricultural Belt`, latitude: d.lat, longitude: d.lon })}
                    className="px-2.5 py-1 rounded-full bg-white/5 hover:bg-emerald/20 border border-white/10 hover:border-emerald/40 text-[11px] text-mineral transition-colors"
                  >
                    {d.name}
                  </button>
                ))}
              </div>
            </div>

          </div>
        </div>
      )}
    </>
  );
};
