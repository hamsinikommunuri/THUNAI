import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { RightPanel } from './components/RightPanel';
import { DashboardView } from './components/DashboardView';
import { DiagnosisFlow } from './components/DiagnosisFlow';
import { WeatherView } from './components/WeatherView';
import { SoilView } from './components/SoilView';
import { CropPlannerView } from './components/CropPlannerView';
import { HistoryView } from './components/HistoryView';
import { ExpertView } from './components/ExpertView';

import { 
  LocationData, 
  WeatherData, 
  SoilProfile, 
  CropRecommendationData, 
  HistoryItem,
  DiagnosisResponse 
} from './types';
import { Language } from './i18n/translations';
import { ThunaiApiClient } from './api/client';

export const App: React.FC = () => {
  const [lang, setLang] = useState<Language>('en');
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [isLocating, setIsLocating] = useState<boolean>(false);
  const [selectedCrop, setSelectedCrop] = useState<string>('tomato');

  // Core Agricultural State
  const [location, setLocation] = useState<LocationData | null>(null);
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [soil, setSoil] = useState<SoilProfile | null>(null);
  const [cropRecs, setCropRecs] = useState<CropRecommendationData | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  // Default fallback coordinates (Coimbatore agricultural tract)
  const DEFAULT_LAT = 11.0168;
  const DEFAULT_LON = 76.9558;
  const DEFAULT_DISTRICT = 'Coimbatore';

  const initDataForLocation = async (lat: number, lon: number, district: string) => {
    try {
      const [wData, sData, hData] = await Promise.all([
        ThunaiApiClient.getWeather(lat, lon, district).catch(() => null),
        ThunaiApiClient.getRegionalSoil(district).catch(() => null),
        ThunaiApiClient.getHistory(10).catch(() => [])
      ]);

      if (wData) setWeather(wData);
      if (sData) setSoil(sData);
      if (hData) setHistory(hData);

      // Fetch crop recommendations based on weather and soil
      const temp = wData ? wData.current.temperature_c : 28.5;
      const soilType = sData ? sData.dominant_soil_type : 'Red Loam';
      const cRecs = await ThunaiApiClient.getCropRecommendations(
        district,
        temp,
        750,
        soilType,
        7.2
      ).catch(() => null);
      if (cRecs) setCropRecs(cRecs);

    } catch (err) {
      console.error('Data initialization error:', err);
    }
  };

  const detectLocation = () => {
    setIsLocating(true);
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const lat = position.coords.latitude;
          const lon = position.coords.longitude;
          try {
            const loc = await ThunaiApiClient.reverseGeocode(lat, lon);
            setLocation(loc);
            await initDataForLocation(lat, lon, loc.district);
          } catch (err) {
            console.warn('Geocoding fallback:', err);
            const fallbackLoc: LocationData = {
              latitude: lat,
              longitude: lon,
              village_or_town: 'Detected GPS Field',
              district: DEFAULT_DISTRICT,
              state: 'Tamil Nadu',
              country: 'India',
              display_name: `Coimbatore Rural (${lat.toFixed(2)}°, ${lon.toFixed(2)}°)`,
              source: 'Browser Geolocation',
              timestamp: new Date().toLocaleTimeString()
            };
            setLocation(fallbackLoc);
            await initDataForLocation(lat, lon, DEFAULT_DISTRICT);
          } finally {
            setIsLocating(false);
          }
        },
        async (error) => {
          console.warn('Geolocation permission denied or unavailable:', error.message);
          // Graceful fallback to default agricultural center
          const fallbackLoc: LocationData = {
            latitude: DEFAULT_LAT,
            longitude: DEFAULT_LON,
            village_or_town: 'Coimbatore',
            district: DEFAULT_DISTRICT,
            state: 'Tamil Nadu',
            country: 'India',
            display_name: 'Coimbatore Agricultural Belt, Tamil Nadu, India',
            source: 'Manual District Default',
            timestamp: new Date().toLocaleTimeString()
          };
          setLocation(fallbackLoc);
          await initDataForLocation(DEFAULT_LAT, DEFAULT_LON, DEFAULT_DISTRICT);
          setIsLocating(false);
        },
        { timeout: 7000 }
      );
    } else {
      // Fallback
      initDataForLocation(DEFAULT_LAT, DEFAULT_LON, DEFAULT_DISTRICT);
      setIsLocating(false);
    }
  };

  useEffect(() => {
    detectLocation();
  }, []);

  const handleDiagnosisComplete = async (res: DiagnosisResponse) => {
    // Refresh history
    try {
      const updatedHistory = await ThunaiApiClient.getHistory(10);
      setHistory(updatedHistory);
    } catch {
      // ignore
    }
  };

  return (
    <div className="min-h-screen bg-[#080B0A] text-[#F4F1E8] flex flex-col font-sans selection:bg-emerald/30 selection:text-white">
      
      {/* Top Navbar */}
      <Navbar
        location={location}
        weather={weather}
        lang={lang}
        onLanguageChange={setLang}
        onLocationUpdate={(newLoc) => {
          setLocation(newLoc);
          initDataForLocation(newLoc.latitude, newLoc.longitude, newLoc.district);
        }}
        onRefreshLocation={detectLocation}
        isLocating={isLocating}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {/* Main Responsive 3-Column Chassis */}
      <div className="flex-1 flex max-w-[1600px] w-full mx-auto">
        
        {/* Left Sidebar (Desktop) */}
        <Sidebar
          activeTab={activeTab}
          onTabChange={setActiveTab}
          lang={lang}
        />

        {/* Center Main Workspace */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto max-w-5xl">
          {activeTab === 'dashboard' && (
            <DashboardView
              location={location}
              weather={weather}
              soil={soil}
              cropRecs={cropRecs}
              history={history}
              onNavigateToTab={setActiveTab}
              onSelectCropForDiagnosis={(cropId) => {
                setSelectedCrop(cropId);
                setActiveTab('vision');
              }}
              lang={lang}
            />
          )}

          {activeTab === 'vision' && (
            <DiagnosisFlow
              initialCrop={selectedCrop}
              location={location}
              weather={weather}
              onDiagnosisComplete={handleDiagnosisComplete}
              lang={lang}
            />
          )}

          {activeTab === 'weather' && (
            <WeatherView
              weather={weather}
              lang={lang}
            />
          )}

          {activeTab === 'soil' && (
            <SoilView
              soil={soil}
              onSoilUpdated={setSoil}
              lang={lang}
            />
          )}

          {activeTab === 'planner' && (
            <CropPlannerView
              cropRecs={cropRecs}
              onSelectCropForDiagnosis={(cropId) => {
                setSelectedCrop(cropId);
                setActiveTab('vision');
              }}
              lang={lang}
            />
          )}

          {activeTab === 'history' && (
            <HistoryView
              history={history}
              onSelectHistoryItem={(item) => {
                setSelectedCrop(item.crop);
                setActiveTab('vision');
              }}
              lang={lang}
            />
          )}

          {activeTab === 'expert' && (
            <ExpertView
              location={location}
              lang={lang}
            />
          )}
        </main>

        {/* Right Information Rail (Desktop XL) */}
        <RightPanel
          weather={weather}
          onNavigateToScanner={() => setActiveTab('vision')}
          onNavigateToWeather={() => setActiveTab('weather')}
          onNavigateToExpert={() => setActiveTab('expert')}
          lang={lang}
        />

      </div>

    </div>
  );
};

export default App;
