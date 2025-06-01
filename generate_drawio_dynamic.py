import xml.etree.ElementTree as ET
import requests
import re
import os
import glob
import base64

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

def main():
  chain_to_drawio("awslambda>awslambda>awsidentityaccessmanagementrole>amazonecsanywhere", "aws_chain_dynamic.drawio")

if __name__ == "__main__":
    main()