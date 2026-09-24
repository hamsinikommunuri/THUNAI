/**
 * THUNAI Multilingual Localization Dictionary (English & Tamil)
 */

export type Language = 'en' | 'ta';

export const translations = {
  en: {
    appName: 'THUNAI',
    appTagline: 'Field Intelligence & Safe Agricultural Decisions',
    heroTitle: 'What does your crop need today?',
    heroSubtitle: 'Capture a leaf photo, inspect real-time weather spray safety, or plan seasonal crops.',
    allowLocation: 'Allow THUNAI to use your location',
    detectedLocation: 'Detected Field Location',
    detectingLocation: 'Detecting GPS location...',
    manualLocationSearch: 'Search district, town or village...',
    lastUpdated: 'Updated',
    
    // Navigation
    navDashboard: 'Farm Today',
    navVision: 'Crop Vision',
    navWeather: 'Weather Shift',
    navSoil: 'Soil Intelligence',
    navPlanner: 'Crop Planner',
    navHistory: 'Scan History',
    navEvidence: 'Evidence Library',
    navExpert: 'Second Opinion',

    // Crops
    cropTomato: 'Tomato',
    cropPotato: 'Potato',
    cropChilli: 'Chilli / Pepper',
    cropPaddy: 'Paddy / Rice',
    cropBanana: 'Banana',

    // Weather & Spray
    sprayNow: 'SPRAY NOW',
    sprayWait: 'WAIT',
    sprayNotRecommended: 'NOT RECOMMENDED',
    optimalWindow: 'Optimal Spray Window',
    rainProbability: 'Rain Probability',
    windSpeed: 'Wind Speed',
    humidity: 'Humidity',

    // Scanner Steps
    stepChooseCrop: '1. Select Crop',
    stepUpload: '2. Upload Photo',
    stepAnalyze: '3. AI Vision',
    stepDiagnosis: '4. Diagnosis',
    stepActions: '5. Action Narrative',
    stepDoseLock: '6. Dose Lock',
    stepWeatherCheck: '7. Weather Shift',
    stepEvidence: '8. Evidence Trace',
    stepExpert: '9. Second Opinion',

    // Dose Lock
    doseLockTitle: 'DOSE LOCK CEREMONY',
    doseLockVerified: 'VERIFIED DOSE',
    doseLockCovenant: 'THUNAI Safety Covenant: We never guess or extrapolate chemical quantities. All doses are locked to statutory CIB&RC and University registries.',
    withholdingPeriod: 'Pre-Harvest Waiting Period',
    days: 'days',

    // Evidence
    evidenceTraceTitle: 'Verifiable Reasoning Chain',
    viewSource: 'View Official Source',
    certifiedBy: 'Validated against',

    // Expert
    expertTitle: 'Agronomist Second Opinion',
    expertNotice: 'When symptoms indicate ambiguity or confidence is low, THUNAI prepares an official Case Dossier for your district KVK extension officer.',
    dispatchDossier: 'Generate & Dispatch Dossier',
    callKvk: 'Call KVK Extension Center',
    kisanCallCenter: 'Kisan Call Center (Toll Free 24x7): 1800-180-1551',

    // Soil
    regionalEstimate: 'Regional Soil Estimate',
    soilTestNotice: 'Regional soil estimate based on ICAR-NBSS&LUP survey. For exact parcel nutrient recommendations, get a laboratory soil test.',
    enterLabTest: 'Enter Soil Health Card Test',
    dominantSoil: 'Dominant Soil Type',
    phLevel: 'Soil pH Range',
    organicCarbon: 'Organic Carbon',
    nitrogen: 'Available Nitrogen',
    phosphorus: 'Available Phosphorus',
    potassium: 'Available Potassium',
    saveMeasurements: 'Apply Lab Measurements',

    // Actions
    runDiagnosis: 'Scan Leaf Now',
    retakeImage: 'Upload Another Photo',
    inspectTrace: 'Inspect Evidence Trace',
    requestOpinion: 'Request Second Opinion',
    uploadHint: 'Drag & drop leaf photo or tap camera to capture',
    acceptedFormats: 'Supported: JPEG, PNG, WEBP (Max 15MB)'
  },
  ta: {
    appName: 'துணை',
    appTagline: 'விவசாயிகளுக்கான பாதுகாப்பான பயிர் நுண்ணறிவு தளம்',
    heroTitle: 'இன்று உங்கள் பயிருக்கு என்ன தேவை?',
    heroSubtitle: 'இலை புகைப்படத்தை பதிவேற்றி நோய் கண்டறிதல், வானிலைக்கேற்ப மருந்து தெளிக்கும் நேரம் மற்றும் மண் வளம் அறியலாம்.',
    allowLocation: 'உங்கள் இருப்பிடத்தை அறிய அனுமதி வழங்கவும்',
    detectedLocation: 'கண்டறியப்பட்ட இருப்பிடம்',
    detectingLocation: 'இருப்பிடம் கண்டறியப்படுகிறது...',
    manualLocationSearch: 'மாவட்டம் அல்லது ஊரின் பெயரை தேடவும்...',
    lastUpdated: 'புதுப்பிக்கப்பட்டது',

    // Navigation
    navDashboard: 'பண்ணை நிலவரம்',
    navVision: 'பயிர் நோய் கண்டறிதல்',
    navWeather: 'வானிலை & தெளிப்பு',
    navSoil: 'மண் வளம்',
    navPlanner: 'பயிர் வழிகாட்டி',
    navHistory: 'முந்தைய பதிவுகள்',
    navEvidence: 'ஆதார நூலகம்',
    navExpert: 'வல்லுநர் கருத்து',

    // Crops
    cropTomato: 'தக்காளி',
    cropPotato: 'உருளைக்கிழங்கு',
    cropChilli: 'மிளகாய்',
    cropPaddy: 'நெல்',
    cropBanana: 'வாழை',

    // Weather & Spray
    sprayNow: 'இப்போது தெளிக்கலாம்',
    sprayWait: 'காத்திருக்கவும்',
    sprayNotRecommended: 'தெளிக்க வேண்டாம்',
    optimalWindow: 'பரிந்துரைக்கப்படும் நேரம்',
    rainProbability: 'மழை வாய்ப்பு',
    windSpeed: 'காற்றின் வேகம்',
    humidity: 'ஈரப்பதம்',

    // Scanner Steps
    stepChooseCrop: '1. பயிரைத் தேர்வு செய்க',
    stepUpload: '2. படம் பதிவேற்றுக',
    stepAnalyze: '3. நுண்ணறிவு ஆய்வு',
    stepDiagnosis: '4. நோய் கணிப்பு',
    stepActions: '5. செய்ய வேண்டியவை',
    stepDoseLock: '6. பூட்டுமுறை அளவு',
    stepWeatherCheck: '7. வானிலை சரிபார்ப்பு',
    stepEvidence: '8. சான்றுகள்',
    stepExpert: '9. வேளாண் வல்லுநர்',

    // Dose Lock
    doseLockTitle: 'பாதுகாப்பான மருந்து அளவு (Dose Lock)',
    doseLockVerified: 'அங்கீகரிக்கப்பட்ட அளவு',
    doseLockCovenant: 'துணை பாதுகாப்பு உறுதிமொழி: நாங்கள் ஒருபோதும் மருந்தளவை தோராயமாக கணிக்க மாட்டோம். அனைத்து அளவுகளும் CIB&RC மற்றும் பல்கலைக்கழக கையேடு வழி அங்கீகரிக்கப்பட்டவை.',
    withholdingPeriod: 'பயன்பாட்டுக்கு முந்தைய இடைவெளி (PHI)',
    days: 'நாட்கள்',

    // Evidence
    evidenceTraceTitle: 'சான்று சங்கிலி (Evidence Trace)',
    viewSource: 'ஆதாரத்தை பார்க்க',
    certifiedBy: 'பரிந்துரைத்த அமைப்பு',

    // Expert
    expertTitle: 'வேளாண் வல்லுநர் மறுஆய்வு',
    expertNotice: 'நோயின் அறிகுறிகள் தெளிவற்றதாக இருந்தால், உங்கள் மாவட்ட கே.வி.கே (KVK) வேளாண் அலுவலருக்கு துணை தளம் அறிக்கை தயாரித்து அளிக்கிறது.',
    dispatchDossier: 'அறிக்கை தயார் செய்க',
    callKvk: 'KVK அலுவலரை அழைக்க',
    kisanCallCenter: 'கிசான் கால் சென்டர் (இலவச அழைப்பு): 1800-180-1551',

    // Soil
    regionalEstimate: 'மண்டல மண் மதிப்பீடு',
    soilTestNotice: 'இது ICAR மண் கணக்கெடுப்பின்படி அமைந்த பிராந்திய மதிப்பீடு. துல்லியமான உர பரிந்துரைக்கு மண் பரிசோதனை செய்யவும்.',
    enterLabTest: 'மண் பரிசோதனை அட்டையை உள்ளிடவும்',
    dominantSoil: 'மண்ணின் வகை',
    phLevel: 'மண் கார அமிலத்தன்மை (pH)',
    organicCarbon: 'கரிம கார்பன்',
    nitrogen: 'தழைச்சத்து (N)',
    phosphorus: 'மணிச்சத்து (P)',
    potassium: 'சாம்பல் சத்து (K)',
    saveMeasurements: 'மதிப்பீட்டை சேமிக்க',

    // Actions
    runDiagnosis: 'பயிரை ஸ்கேன் செய்க',
    retakeImage: 'வேறு படம் எடுக்க',
    inspectTrace: 'ஆதாரங்களை சரிபார்க்க',
    requestOpinion: 'இரண்டாம் கருத்து கேட்க',
    uploadHint: 'இலை படத்தை இழுத்து விடவும் அல்லது கேமரா மூலம் படம் எடுக்கவும்',
    acceptedFormats: 'அனுமதிக்கப்பட்டவை: JPEG, PNG, WEBP (அதிகபட்சம் 15MB)'
  }
};
