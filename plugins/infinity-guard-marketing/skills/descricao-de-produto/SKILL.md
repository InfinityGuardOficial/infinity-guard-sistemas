---
name: descricao-de-produto
description: Páginas de produto e SEO da Infinity Guard na Nuvemshop. Use para escrever ou reescrever a descrição de um produto, o título SEO, a meta description, a descrição curta e o bloco "Compra segura", sempre com preço do catálogo e sem prometer Anatel ou garantia que a loja ainda não documentou.
---

# Descrição de Produto — página que vende sem prometer o que não tem

O cliente de segurança compara antes de comprar. Página com "para quem é", "antes de comprar, confira" e "compra segura" responde as dúvidas que viram WhatsApp e corta devolução por produto errado. Esta skill gera tudo a partir do `catalogo.json` da skill `atendente-infinity-guard`.

Arquivos:
- `scripts/descrever.py`: título SEO (até 60 caracteres), meta description (até 155), descrição curta com Pix e parcelas, e o HTML pronto para o editor da Nuvemshop. Lista as pendências (Anatel, garantia) para o dono.
- `references/categorias.json`: promessa, para quem, como funciona e palavras de SEO por categoria; bloco "Compra segura".

## Modos

### 1. Uma página
```bash
python3 scripts/descrever.py --produto kit-cam-2
```
Cole o HTML no editor da descrição (modo código), o título SEO e a meta description na seção de SEO do produto.

### 2. Todas as páginas
```bash
python3 scripts/descrever.py --todos --saida paginas/
```

### 3. Com prova publicada
Quando o dono tiver o código Anatel conferido e o prazo de garantia por escrito:
```bash
python3 scripts/descrever.py --produto alarme-ikerui --anatel 00000-00-00000 --garantia "12 meses"
```
Depois rode a skill `prova-da-loja` na URL do produto para confirmar que apareceu.

### 4. Texto livre (banner, coleção, página Sobre)
Escreva no mesmo tom (tranquilidade, frases curtas, "segurança onde você estiver") e passe pela skill `revisor-de-promessas` antes de publicar.

## Regras
- Especificação técnica (resolução, alcance, bateria) só do catálogo ou do manual que o dono mandar. Nunca da página do fornecedor sem conferir.
- Tire da página qualquer rastro de fornecedor: "plugue da UE", nome de variante em inglês, marca de outro vendedor (a `prova-da-loja` aponta).
- Foto: produto real, de preferência instalado numa casa brasileira.
- Testes: `python3 -m unittest discover -s tests`.
