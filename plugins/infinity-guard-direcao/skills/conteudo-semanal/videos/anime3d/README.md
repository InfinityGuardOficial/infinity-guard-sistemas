# Vídeos animados (anime 3D) da Infinity Guard

Gera Reels 9:16 no estilo anime 3D (cores chapadas, contorno preto, nuvens de desenho), com narração em
português, legendas sincronizadas, celular, foto real do Maximiliano e cartela com o logo. Tudo roda de graça
no processador: Blender (3D), Kokoro (voz), Skia (textos e efeitos) e ffmpeg.

Primeiro vídeo feito assim: `../eu-tranquei-o-portao/` (73 s).

## Como usar

```bash
videos/anime3d/setup.sh                                  # uma vez por máquina/sessão
videos/anime3d/renderizar.sh videos/eu-tranquei-o-portao # gera videos/eu-tranquei-o-portao/eu-tranquei-o-portao.mp4
```

O render 3D leva cerca de 10 s por quadro (por volta de 1 h e meia para um vídeo de 70 s). Tomadas já
renderizadas ficam em `build/shots/` e são puladas; para refazer uma, apague a pasta dela.
Para conferir antes de renderizar tudo:
`.venv-blender/bin/python <video>/shots3d.py C --still 40 --saida /tmp/teste` (um quadro de uma tomada) e
`python3 <video>/montagem.py still 5 21.5` (quadros da montagem em `build/`).

## Arquivos

| Arquivo | O que faz |
|---|---|
| `lib3d.py` | Biblioteca 3D: materiais toon, carro, casa (com câmera, enfeites de Natal, dia/noite), árvores, estrada, nuvens e os cenários prontos `aerea`, `estrada`, `casa` e `kit`. |
| `narracao.py` | Lê `narracao.json`, gera a voz frase por frase (nenhuma palavra cortada), os tempos de cada frase e a trilha suave. |
| `base.py` | Legendas, textos na tela, celular, foto, efeitos de anime (linhas de impacto, de clima pesado, brilhos), cartela final e a montagem do MP4. |
| `renderizar.sh` | Roda tudo em ordem: narração, tomadas 3D e montagem. |
| `fonts/` | Montserrat e Playfair Display (licença OFL, livre para uso comercial). |

## Novo vídeo

Crie `videos/<nome>/` com três arquivos (copie de `eu-tranquei-o-portao/` e adapte):

1. `narracao.json`: as frases, cada uma com o número da cena. Use `"fala"` quando a voz pronunciar errado
   (ex.: "uótsápi" para WhatsApp, "Massimiliano", "Infíniti Gárd").
2. `shots3d.py`: as tomadas 3D (duração, cenário e parâmetros). Cenários novos entram em `lib3d.py`.
3. `montagem.py`: o que aparece em cada cena por cima do 3D (textos, celular, foto, efeitos).

## Regras que o sistema já segue

- O rosto do Maximiliano aparece só pela foto real (`../ref-maximiliano.jpg`), sem redesenhar. Não há
  versão anime do rosto nem outros personagens.
- Aviso "Narração com voz gerada por IA" na tela. Ao publicar, ligar o rótulo de IA.
- Nada de preço, código da Anatel, guia dos 7 dias, gravação, áudio ou alerta enquanto não estiverem
  confirmados na página. Passar pelo `revisor-de-promessas` antes de impulsionar.
