import xml.etree.ElementTree as ET
import os
import glob
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import json

def fetch_local_service_icons():
    icons = {}
    svg_files = glob.glob(os.path.join("icons_aws", "**", "*.svg"), recursive=True)
    for svg_path in svg_files:
        if "16" in svg_path:
          print(svg_path)  # Mostra o caminho completo do arquivo SVG encontrado
        base = os.path.basename(svg_path)
        # Remove prefix/sufixo e normaliza para chave amigável
        name = base.replace("Res_", "").replace("Arch_", "").replace("_32.svg", "").replace("_48.svg", "").replace(".svg", "")
        key = ''.join(e for e in name.lower() if e.isalnum())
        icons[key] = {
            "svg_path": svg_path,
            "display_name": name
        }
    return icons

service_icons = fetch_local_service_icons()

def generate_icons_markdown(filename="icones.md"):
    icons = fetch_local_service_icons()
    with open(filename, "w", encoding="utf-8") as f:
        f.write("| Referência (key) | Nome do arquivo SVG | Preview |\n")
        f.write("|---|---|---|\n")
        for key, icon in sorted(icons.items()):
            svg_path = icon["svg_path"]
            display_name = os.path.basename(svg_path)
            # Troca extensão para .png para o preview
            png_path = svg_path[:-4] + ".png" if svg_path.lower().endswith(".svg") else svg_path
            # Caminho relativo para o markdown, sempre com barra normal
            rel_png_path = os.path.relpath(png_path).replace("\\", "/")
            f.write(f"| {key} | {display_name} | ![]({rel_png_path}) |\n")

def generate_icons_json(filename="icones.json"):
    icons = fetch_local_service_icons()
    output = []
    for key, icon in sorted(icons.items()):
        svg_path = icon["svg_path"]
        png_path = svg_path[:-4] + ".png" if svg_path.lower().endswith(".svg") else svg_path
        output.append({
            "key": key,
            "resource": ""
        })
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

def delete_16_32_64_icons(base_dir="icons_aws"):
    """
    Remove all files and folders with '16', '32' or '64' in their names under the given base_dir.
    Also removes folders named exactly '16', '32' or '64' and their contents.
    """
    for root, dirs, files in os.walk(base_dir, topdown=False):
        # Remove files with 16, 32 or 64 in their name
        for file in files:
            if any(f"_{size}" in file for size in ["16", "32", "64"]):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Removido: {file_path}")
                except Exception as e:
                    print(f"Erro ao remover {file_path}: {e}")
        # Remove folders named exatamente '16', '32' ou '64' e todo o seu conteúdo
        for dir in dirs:
            if dir in ["16", "32", "64"]:
                dir_path = os.path.join(root, dir)
                import shutil
                try:
                    shutil.rmtree(dir_path)
                    print(f"Pasta removida (com conteúdo): {dir_path}")
                except Exception as e:
                    print(f"Erro ao remover pasta {dir_path}: {e}")

def main():
    print("funcionalidades comentadas")
    #generate_icons_markdown("icones.md")
    #generate_icons_json("icones.json")
    #delete_16_32_64_icons()
    #fetch_aws_resources_md()

if __name__ == "__main__":
    main()