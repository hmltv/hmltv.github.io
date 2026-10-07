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
    print("Generiere XML und ZIPs...")
    
    # Sicherstellen, dass das Haupt-Repo-ZIP existiert
    repo_dir = "repository.hmltv"
    if os.path.exists(repo_dir):
        zip_name = f"{repo_dir}-1.0.5.zip"
        make_zip(repo_dir, os.path.join(repo_dir, zip_name))
        shutil.copy(os.path.join(repo_dir, zip_name), zip_name)

    # Erstelle dieaddons.xml strictly nach Kodi-Standard
    root_xml = ET.Element("addons")
    
    # Gehe durch alle Ordner (Add-ons)
    for folder in os.listdir("."):
        if os.path.isdir(folder) and not folder.startswith(".") and not folder.startswith("_"):
            xml_f = os.path.join(folder, "addon.xml")
            if os.path.exists(xml_f):
                try:
                    # XML einlesen und säubern
                    parser = ET.XMLParser(encoding="utf-8")
                    addon_tree = ET.parse(xml_f, parser=parser)
                    addon_root = addon_tree.getroot()
                    root_xml.append(addon_root)
                except Exception as e:
                    print(f"Fehler bei XML-Parsing in {folder}: {e}")
                    
    #addons.xml schreiben
    xml_str = ET.tostring(root_xml, encoding="utf-8")
    with open("addons.xml", "wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        f.write(xml_str)
        
    # MD5 absolut sauber ohne Zeilenumbrüche oder Zusatzzeichen generieren
    with open("addons.xml", "rb") as f:
        md5_hash = hashlib.md5(f.read()).hexdigest()
    with open("addons.xml.md5", "w", encoding="utf-8") as f:
        f.write(md5_hash.strip())
        
    # index.html für das Kodi Directory Browsing
    with open("index.html", "w", encoding="utf-8") as html:
        html.write('<!DOCTYPE html>\n<html>\n<head><title>HMLTV Repo</title></head>\n<body>\n<h1>HMLTV Kodi Repository</h1>\n')
        if os.path.exists(f"{repo_dir}-1.0.5.zip"):
            html.write(f'<a href="{repo_dir}-1.0.5.zip">{repo_dir}-1.0.5.zip</a><br>\n')
        html.write('</body>\n</html>\n')

if __name__ == "__main__":
    generate_repo()
