import os
import urllib.request
import zipfile
import re
import xml.etree.ElementTree as ET

# Konfiguration der offiziellen Add-on Quellen
ADDONS = {
    "plugin.video.xstream": {
        "zip_url": "https://github.com",
        "is_github_repo_zip": True
    },
    "script.vavoo": {
        "zip_url": "https://github.io", # Beispiel-URL aus Michaz-Umfeld
        "is_github_repo_zip": False
    }
}

def fetch_and_prepare():
    for addon_id, info in ADDONS.items():
        print(f"--- Verarbeite {addon_id} ---")
        os.makedirs(addon_id, exist_ok=True)
        temp_zip = f"temp_{addon_id}.zip"
        
        try:
            # 1. Download des aktuellen ZIPs
            print(f"Lade {addon_id} herunter...")
            urllib.request.urlretrieve(info["zip_url"], temp_zip)
            
            # 2. Entpacken vorbereiten
            extract_to = f"extracted_{addon_id}"
            os.makedirs(extract_to, exist_ok=True)
            
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            
            # 3. Struktur korrigieren (Falls GitHub-Source-ZIP, ist darin oft ein Unterordner "plugin...-master")
            source_dir = extract_to
            if info["is_github_repo_zip"]:
                subdirs = os.listdir(extract_to)
                if subdirs:
                    source_dir = os.path.join(extract_to, subdirs[0])
            
            # 4. addon.xml auslesen, um die exakte Version herauszufinden
            xml_path = os.path.join(source_dir, "addon.xml")
            if not os.path.exists(xml_path):
                print(f"Fehler: Keine addon.xml gefunden für {addon_id} in {xml_path}")
                continue
                
            tree = ET.parse(xml_path)
            root = tree.getroot()
            version = root.get("version")
            print(f"Erkannte Version: {version}")
            
            # 5. Finale ZIP-Datei für das Kodi-Repository erstellen (Kodi verlangt: addonid-version.zip)
            final_zip_name = os.path.join(addon_id, f"{addon_id}-{version}.zip")
            
            with zipfile.ZipFile(final_zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root_dir, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root_dir, file)
                        # Relativen Pfad so setzen, dass im ZIP der Ordnername (addon_id) als Hauptverzeichnis liegt
                        rel_path = os.path.relpath(file_path, source_dir)
                        arc_path = os.path.join(addon_id, rel_path)
                        zipf.write(file_path, arc_path)
            
            # 6. addon.xml, icon.png und fanart.jpg ins Hauptverzeichnis kopieren (für die Repo-Ansicht)
            for file_name in ["addon.xml", "icon.png", "fanart.jpg"]:
                src_file = os.path.join(source_dir, file_name)
                if os.path.exists(src_file):
                    with open(src_file, 'rb') as sf, open(os.path.join(addon_id, file_name), 'wb') as df:
                        df.write(sf.read())
            
            print(f"{addon_id} erfolgreich für Repo vorbereitet.")
            
        except Exception as e:
            print(f"Fehler bei {addon_id}: {str(e)}")
        finally:
            # Aufräumen von temporären Dateien
            if os.path.exists(temp_zip): os.remove(temp_zip)
            import shutil
            if os.path.exists(extract_to): shutil.rmtree(extract_to)

if __name__ == "__main__":
    fetch_and_prepare()
