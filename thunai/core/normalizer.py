"""Entity and chemical normalization for agricultural entities.

Standardizes:
- Crops (Tamil, Tanglish, English, spelling variations -> standard crop_id)
- Problems / Pests / Diseases (Tamil, Tanglish, English -> standard problem_id)
- Chemicals (Brands -> Active ingredient + Formulation + Concentration)
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict


class NormalizedCrop(BaseModel):
    model_config = ConfigDict(frozen=True)
    crop_id: str
    canonical_name: str
    scientific_name: str
    tamil_name: str


class NormalizedProblem(BaseModel):
    model_config = ConfigDict(frozen=True)
    problem_id: str
    canonical_name: str
    tamil_name: str
    crop_id: str
    category: str  # pest, disease, weed, physiological


class NormalizedChemical(BaseModel):
    model_config = ConfigDict(frozen=True)
    raw_input: str
    active_ingredient: str
    formulation: Optional[str] = None
    concentration: Optional[str] = None
    brand_name: Optional[str] = None
    is_known_brand: bool = False


# Supported Phase 1 Crops
SUPPORTED_CROPS: Dict[str, NormalizedCrop] = {
    "paddy": NormalizedCrop(
        crop_id="paddy",
        canonical_name="Paddy",
        scientific_name="Oryza sativa",
        tamil_name="நெல்",
    ),
    "tomato": NormalizedCrop(
        crop_id="tomato",
        canonical_name="Tomato",
        scientific_name="Solanum lycopersicum",
        tamil_name="தக்காளி",
    ),
    "banana": NormalizedCrop(
        crop_id="banana",
        canonical_name="Banana",
        scientific_name="Musa acuminata",
        tamil_name="வாழை",
    ),
    "chilli": NormalizedCrop(
        crop_id="chilli",
        canonical_name="Chilli",
        scientific_name="Capsicum annuum",
        tamil_name="மிளகாய்",
    ),
}

# Crop Aliases across English, Tamil, Tanglish, Spelling Variations
CROP_ALIASES: Dict[str, str] = {
    # Paddy
    "paddy": "paddy",
    "rice": "paddy",
    "nellu": "paddy",
    "nel": "paddy",
    "நெல்": "paddy",
    "அரிசி": "paddy",
    "arisi": "paddy",
    "paddey": "paddy",
    "padi": "paddy",
    "oryza": "paddy",
    "oryza sativa": "paddy",

    # Tomato
    "tomato": "tomato",
    "tomatoes": "tomato",
    "thakkali": "tomato",
    "takali": "tomato",
    "thakali": "tomato",
    "தக்காளி": "tomato",
    "tomatto": "tomato",
    "tomatoe": "tomato",
    "thakkali chedi": "tomato",
    "solanum lycopersicum": "tomato",
    "lycopersicon esculentum": "tomato",

    # Banana
    "banana": "banana",
    "bananas": "banana",
    "plantain": "banana",
    "vazhai": "banana",
    "vaazhai": "banana",
    "valai": "banana",
    "வாழை": "banana",
    "bananna": "banana",
    "vazhaipazham": "banana",
    "வாழை மரம்": "banana",
    "vazhai maram": "banana",
    "musa": "banana",
    "musa acuminata": "banana",

    # Chilli
    "chilli": "chilli",
    "chili": "chilli",
    "chillies": "chilli",
    "chilly": "chilli",
    "milagai": "chilli",
    "milakai": "chilli",
    "mirchi": "chilli",
    "மிளகாய்": "chilli",
    "milagai chedi": "chilli",
    "green chilli": "chilli",
    "capsicum": "chilli",
    "capsicum annuum": "chilli",
}

# Known Brands to Chemical Identity
BRAND_REGISTRY: Dict[str, Tuple[str, str, str]] = {
    # brand: (active_ingredient, formulation, concentration)
    "coragen": ("Chlorantraniliprole", "SC", "18.5%"),
    "confidor": ("Imidacloprid", "SL", "17.8%"),
    "tata mida": ("Imidacloprid", "SL", "17.8%"),
    "tatamida": ("Imidacloprid", "SL", "17.8%"),
    "rogor": ("Dimethoate", "EC", "30%"),
    "monocil": ("Monocrotophos", "SL", "36%"),
    "nuvacron": ("Monocrotophos", "SL", "36%"),
    "furadan": ("Carbofuran", "G", "3%"),
    "roundup": ("Glyphosate", "SL", "41%"),
    "beam": ("Tricyclazole", "WP", "75%"),
    "tilt": ("Propiconazole", "EC", "25%"),
    "bavistin": ("Carbendazim", "WP", "50%"),
    "dithane m-45": ("Mancozeb", "WP", "75%"),
    "dithane": ("Mancozeb", "WP", "75%"),
    "amistar": ("Azoxystrobin", "SC", "23%"),
    "oberon": ("Spiromesifen", "SC", "22.9%"),
    "padan": ("Cartap hydrochloride", "SP", "50%"),
    "regent": ("Fipronil", "SC", "5%"),
    "delegate": ("Spinetoram", "SC", "11.7%"),
    "pegasus": ("Diafenthiuron", "WP", "50%"),
    "fame": ("Flubendiamide", "SC", "39.35%"),
    "blitox": ("Copper oxychloride", "WP", "50%"),
    "actara": ("Thiamethoxam", "WG", "25%"),
    "caldan": ("Cartap hydrochloride", "SP", "50%"),
    "nativo": ("Tebuconazole + Trifloxystrobin", "WG", "50% + 25%"),
    "alika": ("Thiamethoxam + Lambda cyhalothrin", "ZC", "12.6% + 9.5%"),
    "kavach": ("Chlorothalonil", "WP", "75%"),
    "ridomil gold": ("Metalaxyl-M + Mancozeb", "WP", "4% + 64%"),
    "score": ("Difenoconazole", "EC", "25%"),
    "virtako": ("Chlorantraniliprole + Thiamethoxam", "GR", "0.5% + 1%"),
    "ferterra": ("Chlorantraniliprole", "GR", "0.4%"),
    "durmet": ("Chlorpyrifos", "EC", "20%"),
    # Tamil brand and chemical names
    "மோனோசில்": ("Monocrotophos", "SL", "36%"),
    "மோனோகுரோட்டோபாஸ்": ("Monocrotophos", "SL", "36%"),
    "என்டோசல்பான்": ("Endosulfan", "EC", "35%"),
    "பியூரிடான்": ("Carbofuran", "G", "3%"),
    "ரோகார்": ("Dimethoate", "EC", "30%"),
    "ரவுண்டப்": ("Glyphosate", "SL", "41%"),
    "கோரஜென்": ("Chlorantraniliprole", "SC", "18.5%"),
    "கான்பிடார்": ("Imidacloprid", "SL", "17.8%"),
    "பெர்டெர்ரா": ("Chlorantraniliprole", "GR", "0.4%"),
    "டர்மெட்": ("Chlorpyrifos", "EC", "20%"),
    "ஃபோரேட்": ("Phorate", "G", "10%"),
    "மெத்தில் பாராத்தியான்": ("Methyl Parathion", "EC", "50%"),
    "பாராக்குவாட்": ("Paraquat Dichloride", "SL", "24%"),
    "மெத்தோமைல்": ("Methomyl", "SP", "40%"),
    "ட்ரையாசோபாஸ்": ("Triazophos", "EC", "40%"),
}

# Target Problems for the 4 crops
PROBLEM_REGISTRY: Dict[str, NormalizedProblem] = {
    # Paddy
    "paddy_stem_borer": NormalizedProblem(
        problem_id="paddy_stem_borer",
        canonical_name="Yellow Stem Borer",
        tamil_name="தண்டு துளைப்பான்",
        crop_id="paddy",
        category="pest",
    ),
    "paddy_bph": NormalizedProblem(
        problem_id="paddy_bph",
        canonical_name="Brown Planthopper",
        tamil_name="புகையான்",
        crop_id="paddy",
        category="pest",
    ),
    "paddy_leaf_folder": NormalizedProblem(
        problem_id="paddy_leaf_folder",
        canonical_name="Leaf Folder",
        tamil_name="இலை சுருட்டு புழு",
        crop_id="paddy",
        category="pest",
    ),
    "paddy_blast": NormalizedProblem(
        problem_id="paddy_blast",
        canonical_name="Blast Disease",
        tamil_name="குலை நோய்",
        crop_id="paddy",
        category="disease",
    ),
    "paddy_blb": NormalizedProblem(
        problem_id="paddy_blb",
        canonical_name="Bacterial Leaf Blight",
        tamil_name="பாக்டீரியா இலை கருகல்",
        crop_id="paddy",
        category="disease",
    ),
    "paddy_sheath_blight": NormalizedProblem(
        problem_id="paddy_sheath_blight",
        canonical_name="Sheath Blight",
        tamil_name="உறை அழுகல்",
        crop_id="paddy",
        category="disease",
    ),

    # Tomato
    "tomato_fruit_borer": NormalizedProblem(
        problem_id="tomato_fruit_borer",
        canonical_name="Fruit Borer",
        tamil_name="காய் துளைப்பான்",
        crop_id="tomato",
        category="pest",
    ),
    "tomato_early_blight": NormalizedProblem(
        problem_id="tomato_early_blight",
        canonical_name="Early Blight",
        tamil_name="முன் பருவ இலை கருகல்",
        crop_id="tomato",
        category="disease",
    ),
    "tomato_late_blight": NormalizedProblem(
        problem_id="tomato_late_blight",
        canonical_name="Late Blight",
        tamil_name="பின் பருவ இலை கருகல்",
        crop_id="tomato",
        category="disease",
    ),
    "tomato_leaf_curl": NormalizedProblem(
        problem_id="tomato_leaf_curl",
        canonical_name="Leaf Curl Virus",
        tamil_name="இலை சுருள் நோய்",
        crop_id="tomato",
        category="disease",
    ),
    "tomato_whitefly": NormalizedProblem(
        problem_id="tomato_whitefly",
        canonical_name="Whitefly",
        tamil_name="வெள்ளை ஈ",
        crop_id="tomato",
        category="pest",
    ),
    "tomato_red_spider_mite": NormalizedProblem(
        problem_id="tomato_red_spider_mite",
        canonical_name="Red Spider Mite",
        tamil_name="செம்பேன்",
        crop_id="tomato",
        category="pest",
    ),

    # Banana
    "banana_sigatoka": NormalizedProblem(
        problem_id="banana_sigatoka",
        canonical_name="Sigatoka Leaf Spot",
        tamil_name="சிகடோகா இலைப்புள்ளி",
        crop_id="banana",
        category="disease",
    ),
    "banana_panama_wilt": NormalizedProblem(
        problem_id="banana_panama_wilt",
        canonical_name="Panama Wilt",
        tamil_name="பனாமா வாடல் நோய்",
        crop_id="banana",
        category="disease",
    ),
    "banana_aphid": NormalizedProblem(
        problem_id="banana_aphid",
        canonical_name="Banana Aphid",
        tamil_name="வாழை அசுவினி",
        crop_id="banana",
        category="pest",
    ),
    "banana_pseudostem_borer": NormalizedProblem(
        problem_id="banana_pseudostem_borer",
        canonical_name="Pseudostem Borer",
        tamil_name="தண்டு வண்டு",
        crop_id="banana",
        category="pest",
    ),
    "banana_rhizome_weevil": NormalizedProblem(
        problem_id="banana_rhizome_weevil",
        canonical_name="Rhizome Weevil",
        tamil_name="கிழங்கு வண்டு",
        crop_id="banana",
        category="pest",
    ),

    # Chilli
    "chilli_thrips": NormalizedProblem(
        problem_id="chilli_thrips",
        canonical_name="Chilli Thrips",
        tamil_name="இலைப்பேன்",
        crop_id="chilli",
        category="pest",
    ),
    "chilli_anthracnose": NormalizedProblem(
        problem_id="chilli_anthracnose",
        canonical_name="Anthracnose / Fruit Rot",
        tamil_name="கனி அழுகல்",
        crop_id="chilli",
        category="disease",
    ),
    "chilli_yellow_mite": NormalizedProblem(
        problem_id="chilli_yellow_mite",
        canonical_name="Yellow Mite",
        tamil_name="மஞ்சள் பேன்",
        crop_id="chilli",
        category="pest",
    ),
    "chilli_damping_off": NormalizedProblem(
        problem_id="chilli_damping_off",
        canonical_name="Damping Off",
        tamil_name="நாற்று அழுகல்",
        crop_id="chilli",
        category="disease",
    ),
    "chilli_powdery_mildew": NormalizedProblem(
        problem_id="chilli_powdery_mildew",
        canonical_name="Powdery Mildew",
        tamil_name="சாம்பல் நோய்",
        crop_id="chilli",
        category="disease",
    ),
}

# Aliases mapping keywords to (crop_id, problem_id)
PROBLEM_ALIASES: Dict[str, str] = {
    # Paddy
    "stem borer": "paddy_stem_borer",
    "yellow stem borer": "paddy_stem_borer",
    "தண்டு துளைப்பான்": "paddy_stem_borer",
    "thandu thulaippan": "paddy_stem_borer",
    "thandu thulaipan": "paddy_stem_borer",
    "thandu puzhu": "paddy_stem_borer",
    "stemborer": "paddy_stem_borer",
    "குருத்துப்பூச்சி": "paddy_stem_borer",
    "குருத்து பூச்சி": "paddy_stem_borer",
    "kuruthu poochi": "paddy_stem_borer",
    "kuruthupoochi": "paddy_stem_borer",
    "bph": "paddy_bph",
    "brown planthopper": "paddy_bph",
    "brown plant hopper": "paddy_bph",
    "புகையான்": "paddy_bph",
    "pugaiyan": "paddy_bph",
    "pukayan": "paddy_bph",
    "leaf folder": "paddy_leaf_folder",
    "leaf roller": "paddy_leaf_folder",
    "இலை சுருட்டு புழு": "paddy_leaf_folder",
    "ilai suruttu puzhu": "paddy_leaf_folder",
    "ila suruttu": "paddy_leaf_folder",
    "leaffolder": "paddy_leaf_folder",
    "blast": "paddy_blast",
    "blast disease": "paddy_blast",
    "குலை நோய்": "paddy_blast",
    "kula noi": "paddy_blast",
    "kulam noi": "paddy_blast",
    "blast noi": "paddy_blast",
    "bacterial leaf blight": "paddy_blb",
    "blb": "paddy_blb",
    "பாக்டீரியா இலை கருகல்": "paddy_blb",
    "bacterial blight": "paddy_blb",
    "sheath blight": "paddy_sheath_blight",
    "உறை அழுகல்": "paddy_sheath_blight",
    "urai azhugal": "paddy_sheath_blight",

    # Tomato
    "fruit borer": "tomato_fruit_borer",
    "helicoverpa": "tomato_fruit_borer",
    "காய் துளைப்பான்": "tomato_fruit_borer",
    "kai thulaippan": "tomato_fruit_borer",
    "kai thulaipan": "tomato_fruit_borer",
    "fruitborer": "tomato_fruit_borer",
    "tomato borer": "tomato_fruit_borer",
    "early blight": "tomato_early_blight",
    "முன் பருவ இலை கருகல்": "tomato_early_blight",
    "ilai karugal": "tomato_early_blight",
    "earlyblight": "tomato_early_blight",
    "late blight": "tomato_late_blight",
    "பின் பருவ இலை கருகல்": "tomato_late_blight",
    "leaf curl": "tomato_leaf_curl",
    "இலை சுருள் நோய்": "tomato_leaf_curl",
    "ilai surul noi": "tomato_leaf_curl",
    "ilai surul": "tomato_leaf_curl",
    "leaf curl virus": "tomato_leaf_curl",
    "whitefly": "tomato_whitefly",
    "white fly": "tomato_whitefly",
    "வெள்ளை ஈ": "tomato_whitefly",
    "vellai ee": "tomato_whitefly",
    "red spider mite": "tomato_red_spider_mite",
    "spider mite": "tomato_red_spider_mite",
    "செம்பேன்": "tomato_red_spider_mite",
    "semben": "tomato_red_spider_mite",

    # Banana
    "sigatoka": "banana_sigatoka",
    "sigatoka leaf spot": "banana_sigatoka",
    "சிகடோகா இலைப்புள்ளி": "banana_sigatoka",
    "sigatoka ilai pulli": "banana_sigatoka",
    "panama wilt": "banana_panama_wilt",
    "fusarium wilt": "banana_panama_wilt",
    "பனாமா வாடல் நோய்": "banana_panama_wilt",
    "panama vadal": "banana_panama_wilt",
    "vadal noi": "banana_panama_wilt",
    "banana aphid": "banana_aphid",
    "வாழை அசுவினி": "banana_aphid",
    "vazhai asuvini": "banana_aphid",
    "bunchy top": "banana_aphid",
    "pseudostem borer": "banana_pseudostem_borer",
    "தண்டு வண்டு": "banana_pseudostem_borer",
    "thandu vandu": "banana_pseudostem_borer",
    "stem weevil": "banana_pseudostem_borer",
    "vazhai thandu puzhu": "banana_pseudostem_borer",
    "வாழை தண்டு புழு": "banana_pseudostem_borer",
    "vazhai thandu vandu": "banana_pseudostem_borer",
    "வாழை தண்டு வண்டு": "banana_pseudostem_borer",
    "rhizome weevil": "banana_rhizome_weevil",
    "கிழங்கு வண்டு": "banana_rhizome_weevil",
    "kizhangu vandu": "banana_rhizome_weevil",

    # Chilli
    "thrips": "chilli_thrips",
    "chilli thrips": "chilli_thrips",
    "இலைப்பேன்": "chilli_thrips",
    "ilaippen": "chilli_thrips",
    "ilai pen": "chilli_thrips",
    "thripps": "chilli_thrips",
    "anthracnose": "chilli_anthracnose",
    "fruit rot": "chilli_anthracnose",
    "dieback": "chilli_anthracnose",
    "die back": "chilli_anthracnose",
    "கனி அழுகல்": "chilli_anthracnose",
    "kani azhugal": "chilli_anthracnose",
    "yellow mite": "chilli_yellow_mite",
    "chilli mite": "chilli_yellow_mite",
    "மஞ்சள் பேன்": "chilli_yellow_mite",
    "manjal pen": "chilli_yellow_mite",
    "damping off": "chilli_damping_off",
    "damping-off": "chilli_damping_off",
    "நாற்று அழுகல்": "chilli_damping_off",
    "naatru azhugal": "chilli_damping_off",
    "powdery mildew": "chilli_powdery_mildew",
    "சாம்பல் நோய்": "chilli_powdery_mildew",
    "sambal noi": "chilli_powdery_mildew",
}


def normalize_crop(text: Optional[str]) -> Optional[NormalizedCrop]:
    """Normalizes raw crop query/string into a NormalizedCrop or None."""
    if not text:
        return None
    cleaned = text.strip().lower()
    # Direct alias match
    if cleaned in CROP_ALIASES:
        crop_id = CROP_ALIASES[cleaned]
        return SUPPORTED_CROPS.get(crop_id)
    # Match aliases
    for alias, crop_id in CROP_ALIASES.items():
        if any(ord(c) > 127 for c in alias):
            if alias in cleaned:
                return SUPPORTED_CROPS.get(crop_id)
        else:
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, cleaned, re.IGNORECASE):
                return SUPPORTED_CROPS.get(crop_id)
    return None


def normalize_problem(text: Optional[str], crop_id: Optional[str] = None) -> Optional[NormalizedProblem]:
    """Normalizes problem/pest/disease query text into a NormalizedProblem."""
    if not text:
        return None
    cleaned = text.strip().lower()

    # If direct problem_id key provided
    if cleaned in PROBLEM_REGISTRY:
        prob = PROBLEM_REGISTRY[cleaned]
        if crop_id is None or prob.crop_id == crop_id:
            return prob

    # Match aliases
    for alias, prob_id in PROBLEM_ALIASES.items():
        matched = False
        if any(ord(c) > 127 for c in alias):
            matched = alias in cleaned
        else:
            pattern = rf"\b{re.escape(alias)}\b"
            matched = bool(re.search(pattern, cleaned, re.IGNORECASE))
        if matched:
            prob = PROBLEM_REGISTRY[prob_id]
            if crop_id is None or prob.crop_id == crop_id:
                return prob

    # Fallback contextual problem keyword match
    if crop_id == "tomato" and re.search(r"\bborer\b", cleaned):
        return PROBLEM_REGISTRY["tomato_fruit_borer"]
    if crop_id == "paddy" and re.search(r"\bborer\b", cleaned):
        return PROBLEM_REGISTRY["paddy_stem_borer"]
    if crop_id == "banana" and re.search(r"\bborer\b", cleaned):
        return PROBLEM_REGISTRY["banana_pseudostem_borer"]
    if crop_id == "chilli" and re.search(r"\bthri?pps?\b", cleaned):
        return PROBLEM_REGISTRY["chilli_thrips"]

    return None


def normalize_chemical(text: Optional[str]) -> Optional[NormalizedChemical]:
    """Normalizes commercial brand or active ingredient string.

    Separates commercial brand name from active ingredient,
    formulation, and concentration.
    """
    if not text:
        return None
    cleaned = text.strip().lower()

    # Check known brand registry with word boundaries for ASCII
    for brand, (ai, form, conc) in BRAND_REGISTRY.items():
        matched = False
        if any(ord(c) > 127 for c in brand):
            matched = brand in cleaned
        else:
            pattern = rf"\b{re.escape(brand)}\b"
            matched = bool(re.search(pattern, cleaned, re.IGNORECASE))
        if matched:
            return NormalizedChemical(
                raw_input=text,
                active_ingredient=ai,
                formulation=form,
                concentration=conc,
                brand_name=brand.title(),
                is_known_brand=True,
            )

    # If it's already an active ingredient or formulation string
    # e.g. "chlorantraniliprole 18.5% SC" or "imidacloprid"
    # Extract formulation pattern (EC, SC, SL, WP, SP, WG, etc.)
    formulation_match = re.search(r"\b(EC|SC|SL|WP|SP|WG|GR|G|ZC|FS|OD)\b", text, re.IGNORECASE)
    formulation = formulation_match.group(1).upper() if formulation_match else None

    # Extract concentration pattern (e.g. 18.5%, 17.8 SL, 5% SC, 0.4% GR)
    conc_match = re.search(r"(\d+(?:\.\d+)?\s*%)", text)
    concentration = conc_match.group(1).replace(" ", "") if conc_match else None

    # Clean active ingredient by removing formulation and concentration
    ai = text
    if formulation:
        ai = re.sub(rf"\b{formulation}\b", "", ai, flags=re.IGNORECASE)
    if concentration:
        ai = ai.replace(concentration, "")
    ai = re.sub(r"[\d\.\%]", "", ai).strip()

    return NormalizedChemical(
        raw_input=text,
        active_ingredient=ai.strip().title() if ai.strip() else text.strip().title(),
        formulation=formulation,
        concentration=concentration,
        brand_name=None,
        is_known_brand=False,
    )
