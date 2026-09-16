"""Tamil, Tanglish, and English Agricultural Synonym Normalizer."""

import re
from typing import Dict, List, Optional, Set
from thunai.core.enums import CropId


CROP_SYNONYMS: Dict[str, List[str]] = {
    "paddy": [
        "paddy", "nel", "நெல்", "அரிசி", "rice", "oryza", "samba", "kuruvai",
        "thaladi", "nellu", "dhan"
    ],
    "tomato": [
        "tomato", "thakkali", "தக்காளி", "lycopersicon", "solanum lycopersicum",
        "thakkaali", "tamatar"
    ],
    "banana": [
        "banana", "vazhai", "வாழை", "musa", "vaazhai", "vazha", "kela"
    ],
    "chilli": [
        "chilli", "chili", "milagai", "மிளகாய்", "capsicum", "milakai",
        "chillies", "mirchi"
    ],
}

PROBLEM_SYNONYMS: Dict[str, List[str]] = {
    "stem_borer": [
        "stem borer", "yellow stem borer", "stemborer", "குருத்துப்பூச்சி",
        "குருத்துப் பூச்சி", "குருத்து பூச்சி", "kuruthu poochi", "kuruthupoochi",
        "dead heart", "white ear", "scirpophaga incertulas"
    ],
    "blast": [
        "blast", "blast disease", "leaf blast", "neck blast", "குலை நோய்",
        "குலைநோய்", "kulainoi", "kula noi", "magnaporthe oryzae", "pyricularia oryzae"
    ],
    "brown_planthopper": [
        "brown planthopper", "bph", "plant hopper", "புகையான்", "புகையான் பூச்சி",
        "pugaiyan", "hopper burn", "nilaparvata lugens"
    ],
    "fruit_borer": [
        "fruit borer", "fruitborer", "tomato fruit borer", "காய்ப்புழு",
        "காய் புழு", "kaai puzhu", "puzhu", "helicoverpa armigera", "borer"
    ],
    "early_blight": [
        "early blight", "blight", "இலைக்கருகல்", "இலை கருகல்", "இலைக்கருகல் நோய்",
        "ilai karukal", "alternaria solani", "target spot"
    ],
    "late_blight": [
        "late blight", "பிற்பருவ கருகல்", "phytophthora infestans"
    ],
    "sigatoka": [
        "sigatoka", "leaf spot", "sigatoka leaf spot", "இலைப்புள்ளி",
        "இலை புள்ளி", "இலைப்புள்ளி நோய்", "elai pulli", "ilai pulli",
        "pseudocercospora musae", "yellow sigatoka"
    ],
    "pseudostem_borer": [
        "pseudostem borer", "stem weevil", "தண்டு வண்டு", "தண்டு துளைப்பான்",
        "thandu vandu", "thandu thulaippan", "odoiporus longicollis"
    ],
    "panama_wilt": [
        "panama wilt", "fusarium wilt", "wilt", "வாடல் நோய்", "வாடல்நோய்",
        "vadal noi", "fusarium oxysporum"
    ],
    "thrips": [
        "thrips", "chilli thrips", "இலைப்பேன்", "இலை பேன்", "பேன்",
        "ilai pean", "elai paen", "scirtothrips dorsalis", "murungai noi"
    ],
    "anthracnose": [
        "anthracnose", "fruit rot", "die-back", "dieback", "காய் அழுகல்",
        "நுனி கருகல்", "azhukal noi", "colletotrichum capsici"
    ],
}


def tokenize_bilingual(text: str) -> List[str]:
    """Tokenizes mixed Tamil and English text into word tokens."""
    # Match contiguous Tamil characters (\u0B80-\u0BFF), Latin words, and digits
    tokens = re.findall(r"[\u0B80-\u0BFF]+|[A-Za-z0-9]+", text.lower())
    return [t for t in tokens if len(t) > 1]


def expand_synonyms(text: str) -> List[str]:
    """Expands text tokens with known bilingual agricultural synonyms."""
    tokens = tokenize_bilingual(text)
    expanded: Set[str] = set(tokens)
    text_lower = text.lower()

    # Expand crops
    for crop_id, aliases in CROP_SYNONYMS.items():
        matched = False
        for alias in aliases:
            if alias in text_lower or alias in tokens:
                matched = True
                break
        if matched:
            expanded.add(crop_id)
            for alias in aliases:
                expanded.update(tokenize_bilingual(alias))

    # Expand problems
    for problem_id, aliases in PROBLEM_SYNONYMS.items():
        matched = False
        for alias in aliases:
            if alias in text_lower or alias in tokens:
                matched = True
                break
        if matched:
            expanded.add(problem_id)
            for alias in aliases:
                expanded.update(tokenize_bilingual(alias))

    return list(expanded)


class AgriculturalSynonymNormalizer:
    """Normalizes colloquial and multilingual agricultural terms into canonical keys."""

    def __init__(self):
        self.crop_map: Dict[str, CropId] = {}
        for crop_id_str, aliases in CROP_SYNONYMS.items():
            cid = CropId(crop_id_str)
            for alias in aliases:
                self.crop_map[alias.lower().strip()] = cid

        self.problem_map: Dict[str, str] = {}
        for target_key, aliases in PROBLEM_SYNONYMS.items():
            for alias in aliases:
                self.problem_map[alias.lower().strip()] = target_key

    def normalize_crop(self, term: str) -> Optional[CropId]:
        """Maps Tamil, Tanglish, or English crop term to CropId."""
        cleaned = term.lower().strip()
        if cleaned in self.crop_map:
            return self.crop_map[cleaned]

        for alias, cid in self.crop_map.items():
            if alias in cleaned:
                return cid
        return None

    def normalize_target(self, term: str) -> Optional[str]:
        """Maps pest/disease query into canonical target problem identifier."""
        cleaned = term.lower().strip()
        if cleaned in self.problem_map:
            return self.problem_map[cleaned]

        for alias, target in self.problem_map.items():
            if alias in cleaned:
                return target
        return None


def resolve_crop(query: str) -> Optional[str]:
    """Resolves crop id from query string."""
    q_lower = query.lower()
    for crop_id, aliases in CROP_SYNONYMS.items():
        for alias in aliases:
            if re.search(r"\b" + re.escape(alias) + r"\b", q_lower) or alias in q_lower:
                return crop_id
    return None


def resolve_problem(query: str) -> Optional[str]:
    """Resolves target problem id from query string."""
    q_lower = query.lower()
    for problem_id, aliases in PROBLEM_SYNONYMS.items():
        for alias in aliases:
            if alias in q_lower:
                return problem_id
    return None