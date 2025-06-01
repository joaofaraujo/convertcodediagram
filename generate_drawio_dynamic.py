import xml.etree.ElementTree as ET
import requests
import re
import os
import glob
import base64

# AWS4_XML_URL = "https://raw.githubusercontent.com/jgraph/drawio/dev/src/main/webapp/templates/cloud/aws/aws_4.xml"

# def fetch_service_icons():
#     response = requests.get(AWS4_XML_URL)
#     response.raise_for_status()
#     xml_content = response.text
#     tree = ET.ElementTree(ET.fromstring(xml_content))
#     root = tree.getroot()
#     icons = {}
#     for shape in root.findall(".//shape"):
#         name = shape.attrib.get("name", "")
#         key = re.sub(r'[^a-z0-9]', '', name.lower().replace("amazon ", "").replace("aws ", ""))
#         if not key:
#             continue
#         icons[key] = {
#             "shape": "mxgraph.aws4.resourceIcon",
#             "resIcon": f"mxgraph.aws4.{key}",
#             "fillColor": "#FFFFFF"
#         }
#     icons["lambda"] = {"shape": "mxgraph.aws3.lambda_function", "fillColor": "#F58534"}
#     return icons

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

def make_cell(id, value, x, y, width, height, style):
    return f'''<mxCell id="{id}" value="{value}" style="{style};verticalLabelPosition=bottom;verticalAlign=top;labelBackgroundColor=default;aspect=fixed;imageAspect=0;editableCssRules=.*;" vertex="1" parent="1">
  <mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry" />
</mxCell>'''

def make_edge(id, source, target):
    return f'''<mxCell id="{id}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="{source}" target="{target}">
  <mxGeometry relative="1" as="geometry" />
</mxCell>'''

def chain_to_drawio(chain, filename="output.drawio"):
    services = [s.strip().lower() for s in chain.split(">")]
    cells = []
    edges = []
    x = 80
    y = 40
    width = 40
    height = 40
    ids = []
    for idx, s in enumerate(services):
        cell_id = f"n{idx}"
        ids.append(cell_id)
        icon = service_icons.get(s, {})
        if not icon:
            print(f"Serviço '{s}' não encontrado.")
            continue
        with open(icon["svg_path"], "rb") as svg_file:
            svg_data = svg_file.read()
            svg_b64 = base64.b64encode(svg_data).decode("utf-8")
        style = f'shape=image;image=data:image/svg+xml,{svg_b64};'
        cells.append(make_cell(cell_id, icon["display_name"], x, y, width, height, style))
        x += 120
    for i in range(len(ids)-1):
        edges.append(make_edge(f"e{i}", ids[i], ids[i+1]))
    xml = f'''<mxfile>
  <diagram name="Page-1" id="aws-chain">
    <mxGraphModel dx="1000" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        {''.join(cells)}
        {''.join(edges)}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
'''
    with open(filename, "w", encoding="utf-8") as f:
        f.write(xml)

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
            # Caminho relativo para o markdown
            rel_png_path = os.path.relpath(png_path)
            f.write(f"| {key} | {display_name} | ![]({rel_png_path}) |\n")

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
    # print("Lista de serviços disponíveis no service_icons:")
    # for key in sorted(service_icons.keys()):
    #     if "lambda" in key or "ecs" in key:
    #         print(key)
    # chain_to_drawio("awslambda>awslambda>amazonecsanywhere", "aws_chain_dynamic.drawio")
    generate_icons_markdown("icones.md")
    #delete_16_32_64_icons()

if __name__ == "__main__":
    main()