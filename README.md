# Ícones AWS disponíveis para uso no conversor para Drawio

Esta tabela lista todos os ícones disponíveis, o nome de referência (key) para usar no método `chain_to_drawio`, o nome do arquivo SVG e um preview do ícone.

[Ícones encontrados da AWS](https://aws.amazon.com/pt/architecture/icons/)

## Exemplo de uso

Gere diagramas drawio a partir de arquivos Terraform (.tf) ou tfstate (.tfstate) usando este script.

### Para arquivos .tf (Terraform):

```sh
python generate_drawio_dynamic.py --mode tf --input infra/main.tf --output diagrama.drawio
```

### Para arquivos .tfstate (state do Terraform):

```sh
python generate_drawio_dynamic.py --mode tfstate --input infra/terraform_teste.tfstate --output diagrama.drawio --use-generic-circle
```

- O parâmetro `--use-generic-circle` é opcional e, quando usado, desenha um círculo genérico para recursos sem ícone.
- O parâmetro `--output` é opcional e define o nome do arquivo drawio de saída (padrão: `output_from_tf.drawio`).

Abra o arquivo `.drawio` gerado no [draw.io](https://app.diagrams.net/) ou outro editor compatível para visualizar o diagrama.