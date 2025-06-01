import xml.etree.ElementTree as ET
import requests
import re
import os
import glob
import base64
import re
import json

def make_cell(id, value, x, y, width, height, style):
    return f'''<mxCell id="{id}" value="{value}" style="{style};verticalLabelPosition=bottom;verticalAlign=top;labelBackgroundColor=default;aspect=fixed;imageAspect=0;editableCssRules=.*;" vertex="1" parent="1">
  <mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry" />
</mxCell>'''

def make_edge(id, source, target):
    return f'''<mxCell id="{id}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="{source}" target="{target}">
  <mxGeometry relative="1" as="geometry" />
</mxCell>'''

def get_icon_by_field(field, service_icons, key):
    for icon in service_icons:
        if icon.get(field) == key:
            return icon
    return None
  

def chain_to_drawio(service_icons, chain, filename="output.drawio"):
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
        icon = get_icon_by_field("key", service_icons, s)
        if not icon:
            print(f"Serviço '{s}' não encontrado.")
            continue
        with open(icon["svg_path"], "rb") as svg_file:
            svg_data = svg_file.read()
            svg_b64 = base64.b64encode(svg_data).decode("utf-8")
        style = f'shape=image;image=data:image/svg+xml,{svg_b64};'
        cells.append(make_cell(cell_id, icon["key"], x, y, width, height, style))
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

def chain_from_terraform_with_icons(service_icons, filename_tf="infra/main.tf", icons_json="icones.json", filename_drawio="output_from_tf.drawio"):
    """
    Lê o arquivo main.tf, busca ícones correspondentes em icones.json (pelo campo resource) e gera um chain drawio.
    """
    with open(filename_tf, "r", encoding="utf-8") as f:
        tf_content = f.read()
    resource_pattern = re.compile(r'resource\s+"(aws_[a-z0-9_]+)"', re.IGNORECASE)
    services = resource_pattern.findall(tf_content)
    if not services:
        print("Nenhum resource AWS encontrado no main.tf.")
        return
  
    # Cria um dicionário para lookup rápido pelo campo 'resource'
    icon_by_resource = {icon.get("resource", ""): icon for icon in service_icons if icon.get("resource")}
    cells = []
    edges = []
    x = 80
    y = 40
    width = 40
    height = 40
    ids = []
    for idx, resource in enumerate(services):
        cell_id = f"n{idx}"
        ids.append(cell_id)
        icon = get_icon_by_field("resource", service_icons, resource)
        if not icon:
            print(f"Resource '{resource}' não encontrado em icones.json.")
            continue
        svg_path = icon["svg_path"]
        display_name = icon["key"]
        with open(svg_path, "rb") as svg_file:
            svg_data = svg_file.read()
            svg_b64 = base64.b64encode(svg_data).decode("utf-8")
        style = f'shape=image;image=data:image/svg+xml,{svg_b64};'
        cells.append(make_cell(cell_id, display_name, x, y, width, height, style))
        x += 120
    for i in range(len(ids)-1):
        edges.append(make_edge(f"e{i}", ids[i], ids[i+1]))
    xml = f'''<mxfile>\n  <diagram name="Page-1" id="aws-chain">\n    <mxGraphModel dx="1000" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">\n      <root>\n        <mxCell id="0" />\n        <mxCell id="1" parent="0" />\n        {''.join(cells)}\n        {''.join(edges)}\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n'''
    with open(filename_drawio, "w", encoding="utf-8") as f:
        f.write(xml)

def main():
  
  service_icons = []
  with open("icones.json", "r", encoding="utf-8") as f:
        service_icons = json.load(f)
    
  #chain_to_drawio(service_icons, "awslambda>awslambda>awsidentityaccessmanagementrole>amazonecsanywhere", "aws_chain_dynamic.drawio")
  chain_from_terraform_with_icons(service_icons)

if __name__ == "__main__":
    main()