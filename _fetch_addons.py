import os
import urllib.request
import zipfile
import re
import xml.etree.ElementTree as ET
import shutil

# Quellen-Konfiguration mit Live-XML-Auslesung
ADDON_SOURCES = {
    "plugin.video.xstream": {
        "xml_url": "https://githubusercontent.com",
        "zip_url": "https://github.com",
        "is_github": True
    },
    "script.vavoo": {
        "xml_url": "https://github.io", # Scannt Michaz' zentrales Manifest
        "zip_url": "https://github.io",
        "is_github": False
    }
}

def get_latest_version_from_web(addon_id, source_info):
    try:
        req = urllib.request.Request(source_info["xml_url"], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_content = response.read()
            
        if source_info["is_github"]:
            root = ET.fromstring(xml_content)
            return root.get("version")
        else:
            # Für Verzeichnisse: Suchen des Add-ons in der großen addons.xml
            root = ET.fromstring(xml_content)
            for addon in root.findall('addon'):
                if addon.get('id') == addon_id:
                    return addon.get('version')
    except Exception as e:
        print(f"Konnte Live-Version für {addon_id} nicht prüfen: {e}")
    return None

def process_addons():
    for addon_id, info in ADDON_SOURCES.items():
        print(f"\n=== Prüfe {addon_id} ===")
        
        # 1. Live-Version aus dem Internet ermitteln
        latest_version = get_latest_version_from_web(addon_id, info)
        if not latest_version:
            print(f"Überspringe {addon_id}, da keine Version ermittelt werden konnte.")
            continue
            
        target_zip = os.path.join(addon_id, f"{addon_id}-{latest_version}.zip")
        
        # Prüfen, ob wir diese Version schon im Repo haben
        if os.path.exists(target_zip):
            print(f"Version {latest_version} ist bereits aktuell im Repo hinterlegt. Kein Update nötig.")
            continue
            
        print(f"Neue Version erkannt! Installiere {latest_version}...")
        os.makedirs(addon_id, exist_ok=True)
        
        # Alten ZIP-Müll im Ordner aufräumen
        for item in os.listdir(addon_id):
            if item.endswith(".zip"):
                os.remove(os.path.join(addon_id, item))
                
        temp_zip = f"temp_{addon_id}.zip"
        extract_to = f"extracted_{addon_id}"
        
        try:
            # 2. Download der Quelldatei
            req = urllib.request.Request(info["zip_url"], headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(temp_zip, 'wb') as out_file:
                out_file.write(response.read())
                
            # 3. Entpacken
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
                
            # Struktur-Korrektur bei GitHub-Archiven
            source_dir = extract_to
            if info["is_github"]:
                subdirs = os.listdir(extract_to)
                if subdirs:
                    source_dir = os.path.join(extract_to, subdirs[0])
                    # Falls GitHub-Subordner das Add-on tiefer verschachtelt hat
                    if not os.path.exists(os.path.join(source_dir, "addon.xml")):
                        nested = os.path.join(source_dir, addon_id)
                        if os.path.exists(nested): source_dir = nested
            
            # 4. Packe das saubere Kodi-ZIP mit der neuen Versionsnummer
            with zipfile.ZipFile(target_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root_dir, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root_dir, file)
                        rel_path = os.path.relpath(file_path, source_dir)
                        arc_path = os.path.join(addon_id, rel_path)
                        zipf.write(file_path, arc_path)
                        
            # 5. Metadaten-Kopie ins Hauptverzeichnis für Kodi
            for file_name in ["addon.xml", "icon.png", "fanart.jpg"]:
                src_file = os.path.join(source_dir, file_name)
                if os.path.exists(src_file):
                    shutil.copy(src_file, os.path.join(addon_id, file_name))
                    
            print(f"-> {addon_id} erfolgreich auf Version {latest_version} aktualisiert!")
            
        except Exception as e:
            print(f"Fehler bei der Verarbeitung von {addon_id}: {e}")
        finally:
            if os.path.exists(temp_zip): os.remove(temp_zip)
            if os.path.exists(extract_to): shutil.rmtree(extract_to)

if __name__ == "__main__":
    process_addons()
