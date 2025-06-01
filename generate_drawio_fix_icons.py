service_icons = {
    "ecs":  {"shape": "mxgraph.aws4.resourceIcon", "resIcon": "mxgraph.aws4.ecs", "fillColor": "#ED7100"},
    "sqs":  {"shape": "mxgraph.aws4.resourceIcon", "resIcon": "mxgraph.aws4.sqs", "fillColor": "#E7157B"},
    "lambda": {"shape": "mxgraph.aws3.lambda_function", "fillColor": "#F58534"},
}

def make_cell(id, value, x, y, width, height, style):
    return f'''<mxCell id="{id}" value="{value}" style="{style}" vertex="1" parent="1">
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
        if s == "lambda":
            style = f'outlineConnect=0;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;shape={icon["shape"]};fillColor={icon["fillColor"]};gradientColor=none;'
            w = 38.33
        else:
            style = f'sketch=0;outlineConnect=0;fontColor=#232F3E;fillColor={icon["fillColor"]};strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape={icon["shape"]};resIcon={icon.get("resIcon","")};'
            w = width
        cells.append(make_cell(cell_id, s.upper(), x, y, w, height, style))
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

# Exemplo de uso:
chain_to_drawio("ecs>sqs>lambda", "aws_chain.drawio")