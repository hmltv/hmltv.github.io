import os
import zipfile
import hashlib
import xml.etree.ElementTree as ET
import shutil

def make_zip(source_dir, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, os.path.dirname(source_dir))
                zipf.write(file_path, rel_path)

def generate_repo():
    print("Generiere Repo-Struktur nach Michaz-Vorbild...")
    
    # 1. Haupt-Zielordner 'repo' erstellen, falls er nicht existiert
    TARGET_REPO_DIR = "repo"
    os.makedirs(TARGET_REPO_DIR, exist_ok=True)
    
    # 2. Das eigene Repository-Add-on packen und in 'repo/repository.hmltv/' ablegen
    repo_source = "repository.hmltv"
    if os.path.exists(repo_source):
        repo_dest_dir = os.path.join(TARGET_REPO_DIR, repo_source)
        os.makedirs(repo_dest_dir, exist_ok=True)
        
        # addon.xml, icon.png ins Ziel kopieren
        for item in ["addon.xml", "icon.png", "fanart.jpg"]:
            src_f = os.path.join(repo_source, item)
            if os.path.exists(src_f):
                shutil.copy(src_f, os.path.join(repo_dest_dir, item))
        
        # ZIP-Datei im Unterordner erstellen
        zip_name = f"{repo_source}-1.0.6.zip"
        make_zip(repo_source, os.path.join(repo_dest_dir, zip_name))
        
        # Kopie für die Startseite ganz vorne ablegen
        shutil.copy(os.path.join(repo_dest_dir, zip_name), zip_name)

    # 3. xStream und Vavoo in den 'repo'-Ordner verschieben/verarbeiten
    for addon_id in ["plugin.video.xstream", "script.vavoo"]:
        if os.path.exists(addon_id) and addon_id != TARGET_REPO_DIR:
            addon_dest = os.path.join(TARGET_REPO_DIR, addon_id)
            os.makedirs(addon_dest, exist_ok=True)
            
            # Alle Dateien rüberschieben
            for item in os.listdir(addon_id):
                s_item = os.path.join(addon_id, item)
                d_item = os.path.join(addon_dest, item)
                if os.path.isfile(s_item):
                    shutil.copy(s_item, d_item)

    # 4. Zentrale addons.xml IM ORDNER 'repo' generieren
    root_xml = ET.Element("addons")
    
    for folder in os.listdir(TARGET_REPO_DIR):
        folder_path = os.path.join(TARGET_REPO_DIR, folder)
        if os.path.isdir(folder_path):
            xml_f = os.path.join(folder_path, "addon.xml")
            if os.path.exists(xml_f):
                try:
                    parser = ET.XMLParser(encoding="utf-8")
                    addon_tree = ET.parse(xml_f, parser=parser)
                    root_xml.append(addon_tree.getroot())
                except Exception as e:
                    print(f"Fehler bei XML-Parsing in {folder}: {e}")
                    
    # addons.xml in 'repo/' schreiben
    xml_str = ET.tostring(root_xml, encoding="utf-8")
    addons_xml_path = os.path.join(TARGET_REPO_DIR, "addons.xml")
    with open(addons_xml_path, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        f.write(xml_str)
        
    # MD5 in 'repo/' schreiben
    with open(addons_xml_path, "rb") as f:
        md5_hash = hashlib.md5(f.read()).hexdigest()
    with open(os.path.join(TARGET_REPO_DIR, "addons.xml.md5"), "w", encoding="utf-8") as f:
        f.write(md5_hash.strip())
        
    # index.html für Kodi anpassen
    with open("index.html", "w", encoding="utf-8") as html:
        html.write('<!DOCTYPE html>\n<html>\n<head><title>HMLTV Repo</title></head>\n<body>\n<h1>HMLTV Kodi Repository</h1>\n')
        if os.path.exists("repository.hmltv-1.0.6.zip"):
            html.write('<a href="repository.hmltv-1.0.6.zip">repository.hmltv-1.0.6.zip</a><br>\n')
        html.write('</body>\n</html>\n')
    print("Michaz-Struktur erfolgreich aufgebaut!")

if __name__ == "__main__":
    generate_repo()
