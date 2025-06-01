import xml.etree.ElementTree as ET
import requests
import re
import os
import glob
import base64
import re
import json
import argparse

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

def parse_resource_reference(ref_str):
    """
    Recebe uma string como 'aws_iam_policy.dynamodb_policy.arn' e retorna
    {'type': 'aws_iam_policy', 'name': 'dynamodb_policy'}
    """
    parts = ref_str.split('.')
    if len(parts) >= 2:
        return {'type': parts[0], 'name': parts[1]}
    return None
    
def chain_from_terraform_with_icons(service_icons, filename_tf="infra/main.tf", icons_json="icones.json", filename_drawio="output_from_tf.drawio"):
    """
    Lê o arquivo main.tf, busca ícones correspondentes em icones.json (pelo campo resource) e gera um chain drawio.
    Agora considera o tipo e o nome do resource.
    """
    with open(filename_tf, "r", encoding="utf-8") as f:
        tf_content = f.read()
    
    # Regex para pegar resource "aws_tipo" "nome"
    resource_pattern = re.compile(r'resource\s+"(aws_[a-z0-9_]+)"\s+"([a-zA-Z0-9_\-]+)"', re.IGNORECASE)
    matches = resource_pattern.findall(tf_content)
    services = []
    for tipo, nome in matches:
      services.append({'tipo': tipo, 'nome': nome})
    if not services:
        print("Nenhum resource AWS encontrado no main.tf.")
        return
    
    cells = []
    edges = []
    x = 80
    y = 40
    width = 40
    height = 40
    ids = []
    
    for idx, resource_ref in enumerate(services):
        cell_id = f"n{idx}"
        ids.append(cell_id)
        # resource_ref é tipo.nome, então buscamos pelo campo resource
        icon = get_icon_by_field("resource", service_icons, resource_ref['tipo'])
        if not icon:
            print(f"Resource '{resource_ref['tipo']}' não encontrado em icones.json.")
            continue
        svg_path = icon["svg_path"]
        display_name = icon["key"]
        with open(svg_path, "rb") as svg_file:
            svg_data = svg_file.read()
            svg_b64 = base64.b64encode(svg_data).decode("utf-8")
        style = f'shape=image;image=data:image/svg+xml,{svg_b64};'
        cells.append(make_cell(cell_id, display_name, x, y, width, height, style))
        x += 120
        
    xml = f'''<mxfile>\n  <diagram name="Page-1" id="aws-chain">\n    <mxGraphModel dx="1000" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">\n      <root>\n        <mxCell id="0" />\n        <mxCell id="1" parent="0" />\n        {''.join(cells)}\n        {''.join(edges)}\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n'''
    with open(filename_drawio, "w", encoding="utf-8") as f:
        f.write(xml)

def chain_from_tfstate_with_icons(service_icons, filename_tfstate="infra/terraform.tfstate", filename_drawio="output_from_tfstate.drawio", use_generic_circle=True):
    """
    Lê o arquivo terraform_teste.tfstate, busca ícones correspondentes em icones.json (pelo campo resource) e gera um drawio.
    Usa os dependencies para fazer os edges entre os elementos.
    Se use_generic_circle=True, usa um círculo nativo do draw.io quando não encontrar ícone.
    Se use_generic_circle=False, ignora recursos sem ícone.
    """
    with open(filename_tfstate, "r", encoding="utf-8") as f:
        tfstate = json.load(f)

    resources = tfstate.get("resources", [])
    resource_id_map = {}
    cells = []
    edges = []
    x = 80
    y = 40
    width = 40
    height = 40
    ids = []
    # 1. Distribuição em grid: calcula linhas e colunas para melhor visualização
    import math
    total = len([res for res in resources if get_icon_by_field("resource", service_icons, res.get("type")) or use_generic_circle])
    cols = math.ceil(math.sqrt(total))
    spacing_x = 120
    spacing_y = 120
    x0 = 80
    y0 = 40
    x = x0
    y = y0
    cell_count = 0
    # 2. Criação dos nós e mapeamento
    resource_id_map.clear()
    cells.clear()
    ids.clear()
    for idx, res in enumerate(resources):
        tipo = res.get("type")
        nome = res.get("name")
        resource_id = f"{tipo}.{nome}"
        icon = get_icon_by_field("resource", service_icons, tipo)
        if icon or use_generic_circle:
            cell_id = f"n{idx}"
            resource_id_map[resource_id] = cell_id
            ids.append(cell_id)
            if icon:
                svg_path = icon["svg_path"]
                display_name = res.get("name")
                with open(svg_path, "rb") as svg_file:
                    svg_data = svg_file.read()
                    svg_b64 = base64.b64encode(svg_data).decode("utf-8")
                style = f'shape=image;image=data:image/svg+xml,{svg_b64};'
            else:
                style = 'ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;strokeWidth=2;'
                display_name = tipo
            cells.append(make_cell(cell_id, display_name, x, y, width, height, style))
            cell_count += 1
            if cell_count % cols == 0:
                x = x0
                y += spacing_y
            else:
                x += spacing_x
    # 3. Criação dos edges baseados em dependencies
    edges.clear()
    for idx, res in enumerate(resources):
        tipo = res.get("type")
        nome = res.get("name")
        resource_id = f"{tipo}.{nome}"
        cell_id = resource_id_map.get(resource_id)
        if not cell_id:
            continue
        for instance in res.get("instances", []):
            dependencies = instance.get("dependencies", [])
            for dep in dependencies:
                dep_cell_id = resource_id_map.get(dep)
                if dep_cell_id:
                    edges.append(make_edge(f"e{len(edges)}", dep_cell_id, cell_id))
    xml = f'''<mxfile>\n  <diagram name="Page-1" id="aws-chain">\n    <mxGraphModel dx="1000" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">\n      <root>\n        <mxCell id="0" />\n        <mxCell id="1" parent="0" />\n        {''.join(cells)}\n        {''.join(edges)}\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n'''
    with open(filename_drawio, "w", encoding="utf-8") as f:
        f.write(xml)

def main():
    parser = argparse.ArgumentParser(description="Gera diagrama drawio a partir de arquivos Terraform ou tfstate.")
    parser.add_argument('--mode', choices=['tf', 'tfstate'], required=True, help='Modo de leitura: tf (arquivo .tf) ou tfstate (arquivo .tfstate)')
    parser.add_argument('--input', required=True, help='Caminho do arquivo a ser lido (.tf ou .tfstate)')
    parser.add_argument('--output', default='solution_architect.drawio', help='Caminho do arquivo drawio de saída')
    parser.add_argument('--use-generic-circle', action='store_true', help='Usa círculo genérico para recursos sem ícone (apenas para tfstate)')
    args = parser.parse_args()

    with open("icones.json", "r", encoding="utf-8") as f:
        service_icons = json.load(f)

    if args.mode == 'tf':
        chain_from_terraform_with_icons(service_icons, filename_tf=args.input, filename_drawio=args.output)
    elif args.mode == 'tfstate':
        chain_from_tfstate_with_icons(service_icons, filename_tfstate=args.input, filename_drawio=args.output, use_generic_circle=args.use_generic_circle)

if __name__ == "__main__":
    main()