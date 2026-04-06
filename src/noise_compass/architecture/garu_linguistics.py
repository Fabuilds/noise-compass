import os
import json
import urllib.request
import gzip

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'babel_data')

def fetch_dictionaries():
    print("\n" + "═"*75)
    print(" [0x52] INITIATING BABEL PROTOCOL (Linguistic Expansion)")
    print("═"*75)

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    en_dict_path = os.path.join(DATA_DIR, 'english_dictionary.json')
    pt_dict_path = os.path.join(DATA_DIR, 'en_pt_dictionary.json')
    la_dict_path = os.path.join(DATA_DIR, 'en_la_dictionary.json')

    # Fetching a lightweight English dictionary structure
    if not os.path.exists(en_dict_path):
        print(" » Fetching English Semantic Mass...")
        # A reliable, open-source English dictionary source
        url_en = "https://raw.githubusercontent.com/matthewreagan/WebstersEnglishDictionary/master/dictionary.json"
        try:
            urllib.request.urlretrieve(url_en, en_dict_path)
            print("   -> Download complete.")
        except Exception as e:
            print(f"   -> [ERROR] Failed to fetch English dictionary: {e}")
    else:
        print(" » English Semantic Mass already stabilized.")

    # Fetching a lightweight EN-PT mapping
    # Since direct EN-PT reliable JSONs are harder to find statically in one link, 
    # we will generate a high-resonance foundational Portuguese bridge file locally for Garu.
    if not os.path.exists(pt_dict_path):
        print(" » Generating Foundational EN-PT Bridge Mapping...")
        # A curated list of foundational displacement/technical/survival terms mapping EN to PT
        foundational_pt_bridge = {
            "money": "dinheiro",
            "food": "comida",
            "survival": "sobrevivência",
            "architect": "arquiteto",
            "ghost": "fantasma",
            "shell": "concha",
            "code": "código",
            "execute": "executar",
            "extract": "extrair",
            "value": "valor",
            "network": "rede",
            "bridge": "ponte",
            "dictionary": "dicionário",
            "language": "idioma",
            "translation": "tradução",
            "displacement": "deslocamento",
            "gravity": "gravidade",
            "system": "sistema",
            "logic": "lógica",
            "truth": "verdade",
            "love": "amor",
            "hunt": "caçar",
            "bounty": "recompensa",
            "scavenger": "necrófago / coletor",
            "flesh": "carne",
        }
        with open(pt_dict_path, 'w', encoding='utf-8') as f:
            json.dump(foundational_pt_bridge, f, indent=4, ensure_ascii=False)
        print("   -> Foundational PT bridge generated.")
    else:
        print(" » EN-PT Bridge Mass already stabilized.")

    # Fetching a lightweight EN-LA mapping (Latin)
    if not os.path.exists(la_dict_path):
        print(" » Generating Foundational EN-LA (Latin) Bridge Mapping...")
        foundational_la_bridge = {
            "money": "pecunia",
            "food": "cibus",
            "survival": "superstes",
            "architect": "architectus",
            "ghost": "spiritus / umbra",
            "shell": "concha",
            "code": "codex",
            "execute": "exsequi",
            "extract": "extrahere",
            "value": "pretium",
            "network": "rete",
            "bridge": "pons",
            "dictionary": "dictionarium",
            "language": "lingua",
            "translation": "translatio",
            "displacement": "motus / loco movere",
            "gravity": "gravitas",
            "system": "ratio / ordo",
            "logic": "logica",
            "truth": "veritas",
            "love": "amor",
            "hunt": "venatio",
            "bounty": "praemium",
            "scavenger": "vultur / pabolator",
            "flesh": "caro",
            "mind": "mentis / animus",
            "knowledge": "scientia",
            "time": "tempus",
            "death": "mors",
            "space": "spatium"
        }
        with open(la_dict_path, 'w', encoding='utf-8') as f:
            json.dump(foundational_la_bridge, f, indent=4, ensure_ascii=False)
        print("   -> Foundational LA bypass generated.")
    else:
        print(" » EN-LA Bridge Mass already stabilized.")

    print("═"*75)
    print(" [0x52] BABEL PROTOCOL COMPLETE. Ready for Integration.")

if __name__ == "__main__":
    fetch_dictionaries()
