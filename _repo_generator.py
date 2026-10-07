import os
import zipfile
import hashlib
import xml.etree.ElementTree as ET

def make_zip(source_dir, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, os.path.dirname(source_dir))
                zipf.write(file_path, rel_path)

def generate_repo():
    print("Starte manuelles Verpacken...")
    
    repo_dir = "repository.hmltv"
    zip_name = ""
    
    if os.path.exists(repo_dir):
        xml_path = os.path.join(repo_dir, "addon.xml")
        if os.path.exists(xml_path):
            tree = ET.parse(xml_path)
            root = tree.getroot()
            version = root.get("version", "1.0.2")
            
            zip_name = f"{repo_dir}-{version}.zip"
            output_path = os.path.join(repo_dir, zip_name)
            
            # ZIP direkt im Unterordner erstellen
            make_zip(repo_dir, output_path)
            
            # WICHTIG: Eine Kopie der ZIP direkt ins Hauptverzeichnis legen, damit Kodi sie sofort sieht!
            import shutil
            shutil.copy(output_path, zip_name)
            print(f"Erfolgreich erstellt und kopiert: {zip_name}")
        else:
            print(f"Fehler: Keine addon.xml im Ordner {repo_dir} gefunden!")
    else:
        print(f"Fehler: Ordner {repo_dir} existiert nicht!")

    # Zentrale Manifest-Dateien erstellen
    root_xml = ET.Element("addons")
    for folder in os.listdir("."):
        if os.path.isdir(folder) and not folder.startswith(".") and not folder.startswith("_"):
            xml_f = os.path.join(folder, "addon.xml")
            if os.path.exists(xml_f):
                try:
                    addon_tree = ET.parse(xml_f)
                    root_xml.append(addon_tree.getroot())
                except Exception as e:
                    print(f"Fehler beim Lesen von {xml_f}: {e}")
                    
    with open("addons.xml", "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        f.write(ET.tostring(root_xml, encoding="utf-8").decode("utf-8"))
        
    with open("addons.xml", "rb") as f:
        md5_hash = hashlib.md5(f.read()).hexdigest()
    with open("addons.xml.md5", "w", encoding="utf-8") as f:
        f.write(md5_hash)
        
    # JETZT BORT DAS SKRIPT DIE STARTSEITE FÜR KODI
    if zip_name:
        with open("index.html", "w", encoding="utf-8") as html:
            html.write(f'<!DOCTYPE html>\n<html>\n<head><title>HMLTV Repo</title></head>\n<body>\n')
            html.write(f'<h1>HMLTV Kodi Repository</h1>\n')
            html.write(f'<a href="{zip_name}">{zip_name}</a>\n')
            html.write(f'</body>\n</html>\n')
        print("index.html für Kodi erfolgreich generiert!")

if __name__ == "__main__":
    generate_repo()
