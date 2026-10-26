# Comerciais 3D da Infinity Guard (9:16)

Pipeline para comerciais curtos em animação 3D com **personagens fictícios brasileiros**, cenas de bairro
brasileiro, formato vertical 1080x1920 e CTA para **infinityguard.com.br**. Usa o motor gratuito de
`../anime3d/` (Blender, voz Kokoro, Skia, ffmpeg) e roda no processador.

## Episódios

| Pasta | Título | Situação |
|---|---|---|
| `ep15-quem-deixou-isso-na-porta/` | Quem deixou isso na porta? (50 s) | roteiro, storyboard, legendas e render prontos; narração **provisória** (sem Dave) |
| `ep16-o-cliente-chegou-antes/` | O cliente chegou antes de todo mundo! (50 s, loja de bairro) | pronto, com efeitos sonoros, cortes de câmera e personagens mais expressivos; narração **provisória** (sem Dave) |
| `ep17-o-presente-que-ninguem-esperava/` | O presente que ninguém esperava (55 s, fechadura preta) | pronto, com capa 9:16, packshot com a foto real e preço falado do catálogo; narração **provisória** (sem Dave) |
| `ep18-o-primeiro-presente-da-loja/` | O primeiro presente da loja (55 s, câmera dome ASECAM) | pronto, com capa, descrição do post e arquivo de projeto; selo Black Friday sem oferta; narração **provisória** (sem Dave) |
| `ep19-o-misterio-das-plantas/` | O mistério das plantas (55 s, Câmera ASECAM PTZ 4K 8MP) | pronto, com capa, descrição e arquivo de projeto; app ilustrativo; narração **provisória** (sem Dave) | aguardando `episodios.md` (não existe no repositório) |

Cenários prontos: `varanda` (casa térrea com porta, encomenda e vizinho), `loja` (comércio de bairro com porta de
enrolar, caixa e área privada) e `kit_dupla` (o produto no pedestal). Efeitos sonoros e ambiente saem de `sons.py`
(lista `"sons"` no episodio.json). Opções do episodio.json: `tomadas` (vários cortes por segmento), `logo`
(`circular` ou horizontal), `mostrar_frete` (só o cálculo por CEP, que é o que o catálogo confirma),
`tomada_produto` e `qualidade` (`samples`, `resolucao_3d`).

Cada episódio é uma pasta com três arquivos escritos à mão:

| Arquivo | O que tem |
|---|---|
| `episodio.json` | Fonte única do episódio: segmentos com tempo fixo, ação, câmera, falas (quem fala e quando), textos de tela, produto (id do catálogo), site e CTA. |
| `shots3d.py` | As tomadas 3D (duração, cenário e parâmetros). |
| `montagem.py` | Desenhos próprios do episódio por cima do 3D (ex.: close da etiqueta). |

E o pipeline gera: `storyboard.md` (com um quadro por segmento), `roteiro_de_cenas.md`, `legendas.srt`,
`build/` (áudio, tomadas, vídeo) e, se tudo passar, `exports/<episodio>[_PROVISORIO].mp4` + `.srt`.

## Como rodar

```bash
../anime3d/setup.sh                                   # uma vez
python3 produzir.py tudo ep15-quem-deixou-isso-na-porta
```

Ou por etapa: `validar` → `narrar` → `documentos` → `render` → `checar` → `exportar`.
O render 3D leva por volta de 2 h por episódio de 50 s; tomadas prontas são puladas.

## O que é validado

**Antes do render** (`validar`, roda em segundos):
- o produto existe e está ativo no catálogo único (`skills/atendente-infinity-guard/references/catalogo.json`);
- o catálogo tem no máximo 7 dias (senão, atualize com a skill `catalogo-e-precos`);
- nenhuma fala ou texto de tela cita gravação, áudio, alerta, notificação, aplicativo, Anatel, garantia,
  instalação, 4G, frete, promoção, "sem juros", resolução (2K/4K/Full HD), nuvem, "100%", identificação ou
  reconhecimento de pessoas, nem o proprietário;
- recursos da câmera citados (visão noturna, dupla lente, Wi-Fi, zoom...) estão no nome ou nos destaques do
  produto no catálogo;
- nenhum preço escrito à mão: preço, Pix e parcelas saem do catálogo, com a data;
- os segmentos cobrem 0 até a duração sem buracos, cada fala cai no seu segmento, há encerramento com site, logo e CTA.

**Na narração** (`narrar`): cada fala tem que terminar antes da próxima e antes do fim do segmento.

**Depois do render** (`checar`): 1080x1920, duração certa (±0,3 s), volume entre -17 e -12 LUFS sem
estouro, nenhuma fala passando do segmento, nenhum trecho preto. `exportar` só copia se `validar` e `checar` passarem.

Testes do validador: `python3 -m unittest discover -s tests`.

## Voz Dave

A Dave é uma voz do Pippit e **não está disponível neste ambiente** (não há ferramenta de áudio com a Dave
configurada). Para usar a Dave:

1. No Pippit, gere cada fala do **narrador** do `episodio.json`, na ordem, e exporte em WAV.
2. Salve em `<episodio>/voz_dave/01.wav`, `02.wav`, ... e crie `voz_dave/AUTORIZACAO.txt` dizendo quem
   autorizou o uso da voz.
3. Rode `python3 produzir.py narrar <episodio>` e depois `render` (só a montagem é refeita, em minutos).

Sem isso, o narrador sai com a voz gratuita Kokoro como **provisória**: o vídeo mostra "vozes sintéticas
provisórias" e o arquivo exportado leva `_PROVISORIO` no nome. Os personagens (Ana, Marcos, Seu Joaquim)
usam vozes Kokoro de personagem.

## Regras fixas

- Personagens fictícios, sem rosto nem avatar do proprietário.
- Câmera mostrada em posição adequada, com o campo de visão cobrindo só a entrada da própria casa.
- Nada de consulta de imagens no aplicativo enquanto a função não estiver confirmada no catálogo.
- Nunca dizer que a câmera identificou alguém se isso não foi mostrado.
- O modelo 3D da câmera é **ilustrativo** (o cartão do produto diz "Imagem ilustrativa").
- Antes de publicar: reconferir o preço no site e passar o texto pelo `revisor-de-promessas`.
