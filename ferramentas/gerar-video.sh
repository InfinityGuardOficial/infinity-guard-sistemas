#!/usr/bin/env bash
# Gerador do Reel (9:16, 30 fps) da Infinity Guard — versão nuvem (Linux) do gerar-video.ps1.
# Uso: bash ferramentas/gerar-video.sh roteiro.txt saida.mp4
# roteiro.txt (uma linha por campo; foto= e tela= podem repetir):
#   foto=acervo/loja/ptz4k/1.jpg
#   tela=KICKER|texto curto da tela         (4 a 6 telas, a 1ª é o gancho)
#   produto=Câmera ASECAM PTZ 4K 8MP        (opcional; sem preço não há tela de oferta)
#   preco=R$ 1.899,06 no Pix
#   parcelas=ou R$ 2.110,07 em até 12x
#   cta=Compre pelo site
# Visual: gancho no 1º segundo, kicker dourado + frase forte, texto com movimento, foto com movimento de câmera,
# barra de progresso, transições deslizando, tela de oferta e fechamento com logo, site e slogan.
set -euo pipefail
ROT="$1"; SAIDA="$2"
AQUI="$(cd "$(dirname "$0")/.." && pwd)"
FF="${FFMPEG:-ffmpeg}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
OURO=0xD4AF5F; NAVY=0x06121F

# caminhos: no Windows (Git Bash) o ffmpeg nativo precisa de C:/...
win(){ if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s' "$1"; fi; }
fx(){ local p; p="$(win "$1")"; printf '%s' "${p//:/\\:}"; }   # para usar dentro de filtros
fonte(){ fc-match -f '%{file}' "$1" 2>/dev/null || true; }
FH="${FONT_H:-$(fonte 'Inter:bold')}"; [ -n "$FH" ] || FH="$(fonte 'DejaVu Sans:bold')"
FK="${FONT_K:-$(fonte 'Inter:semibold')}"; [ -n "$FK" ] || FK="$FH"
FR="${FONT_R:-$(fonte 'Inter')}"; [ -n "$FR" ] || FR="$(fonte 'DejaVu Sans')"
FH="$(fx "$FH")"; FK="$(fx "$FK")"; FR="$(fx "$FR")"
LOGO="$AQUI/acervo/marca/logo.png"
ENC=(-c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30)

fotos=(); telas=(); produto=""; preco=""; parcelas=""; cta="Compre pelo site"
while IFS= read -r l || [ -n "$l" ]; do
  l="${l%$'\r'}"; k="${l%%=*}"; v="${l#*=}"
  case "$k" in foto) fotos+=("$v");; tela) telas+=("$v");; produto) produto="$v";; preco) preco="$v";; parcelas) parcelas="$v";; cta) cta="$v";; esac
done < "$ROT"
[ ${#telas[@]} -gt 0 ] || { echo "sem telas" >&2; exit 1; }

arq(){ local f; f="$(mktemp "$TMP/tXXXXXXXX.txt")"; printf '%s' "$1" > "$f"; fx "$f"; }
quebra(){ echo "$1" | fold -s -w "$2" | sed 's/ *$//'; }
# Texto que entra subindo e aparecendo: anim fonte texto tamanho cor y atraso
anim(){ local a="min(1\\,max(0\\,(t-$6)/0.35))"
  printf "drawtext=fontfile='%s':textfile='%s':expansion=none:fontsize=%s:fontcolor=%s:x=(w-text_w)/2:y=%s+36*(1-%s):alpha='%s':shadowcolor=black@0.55:shadowx=0:shadowy=4" "$1" "$(arq "$2")" "$3" "$4" "$5" "$a" "$a"; }
# Bloco centralizado linha a linha; devolve filtro em BLOCO_F e altura em BLOCO_H
bloco(){ local t="$1" max="$2" tam="$3" cor="$4" y0="$5" at="$6" i=0 out="" alt=$(( $3 * 118 / 100 ))
  while IFS= read -r linha; do [ -z "$linha" ] && continue
    [ -n "$out" ] && out+=","
    out+="$(anim "$FH" "$linha" "$tam" "$cor" $((y0 + i*alt)) "$(awk "BEGIN{print $at+0.08*$i}")")"; i=$((i+1))
  done < <(quebra "$t" "$max")
  BLOCO_F="$out"; BLOCO_H=$((i*alt)); }

# Fotos: corta as faixas brancas (quadrado central) e padroniza 1080x1080
fs=(); i=0
for f in "${fotos[@]}"; do
  src="$f"; [ -f "$src" ] || src="$AQUI/$f"; [ -f "$src" ] || continue
  "$FF" -hide_banner -loglevel error -y -i "$(win "$src")" -vf "crop='min(iw\,ih)':'min(iw\,ih)',scale=1080:1080" "$(win "$TMP/f$i.jpg")" && fs+=("$TMP/f$i.jpg") && i=$((i+1))
done
[ ${#fs[@]} -gt 0 ] || { echo "nenhuma foto utilizável" >&2; exit 1; }
"$FF" -hide_banner -loglevel error -y -f lavfi -i "color=black:s=1080x1000,format=rgba" -vf "geq=r=0:g=0:b=0:a='255*pow(Y/H\,1.3)*0.92'" -frames:v 1 "$(win "$TMP/grad.png")"

segs=(); durs=()
for k in "${!telas[@]}"; do
  [ "$k" -ge 6 ] && break
  kick="${telas[$k]%%|*}"; txt="${telas[$k]#*|}"; [ "$kick" = "${telas[$k]}" ] && kick=""
  foto="${fs[$(( k % ${#fs[@]} ))]}"
  if [ "$k" -eq 0 ]; then d=2.6; tam=84; mx=20; else d=2.4; tam=72; mx=23; fi
  if [ $((k % 2)) -eq 0 ]; then z="1+0.06*t/$d"; else z="1.08-0.06*t/$d"; fi
  bloco "$txt" "$mx" "$tam" white 1360 0.18
  kf=""; [ -n "$kick" ] && kf="$(anim "$FK" "$(echo "$kick" | tr '[:lower:]' '[:upper:]')" 40 "$OURO" 1290 0.05),"
  fc="[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness=-0.5:saturation=0.8[bg];"
  fc+="[b]scale=w='trunc(1080*($z)/2)*2':h=-2:eval=frame[ph];[bg][ph]overlay=x=(W-w)/2:y=260+(1080-h)/2[v1];"
  fc+="[1:v]format=rgba[gr];[v1][gr]overlay=0:920[v2];[v2]${kf}${BLOCO_F},"
  fc+="drawbox=x=480:y=$((1360+BLOCO_H+28)):w=120:h=6:color=${OURO}:t=fill:enable='gte(t\,0.45)',"
  fc+="drawtext=fontfile='$FK':text='INFINITY GUARD':fontsize=30:fontcolor=${OURO}@0.9:x=(w-text_w)/2:y=1830,format=yuv420p[v]"
  "$FF" -hide_banner -loglevel error -y -loop 1 -t "$d" -i "$(win "$foto")" -loop 1 -t "$d" -i "$(win "$TMP/grad.png")" -filter_complex "$fc" -map '[v]' "${ENC[@]}" "$(win "$TMP/s$k.mp4")"
  segs+=("$TMP/s$k.mp4"); durs+=("$d")
done

if [ -n "$preco" ]; then
  d=2.8; bloco "$produto" 22 58 white 1290 0.15
  fc="[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=34:2,eq=brightness=-0.55[bg];"
  fc+="[1:v]scale=w='trunc(760*(1+0.04*t/$d)/2)*2':h=-2:eval=frame[ph];[bg][ph]overlay=x=(W-w)/2:y=330[v1];"
  fc+="[v1]$(anim "$FK" 'OFERTA INFINITY GUARD' 40 "$OURO" 1210 0.05),${BLOCO_F},"
  fc+="drawbox=x=140:y=$((1290+BLOCO_H+30)):w=800:h=130:color=${OURO}:t=fill:enable='gte(t\,0.4)',"
  fc+="drawtext=fontfile='$FH':textfile='$(arq "$preco")':fontsize=72:fontcolor=${NAVY}:x=(w-text_w)/2:y=$((1290+BLOCO_H+52)):enable='gte(t\,0.4)',"
  [ -n "$parcelas" ] && fc+="drawtext=fontfile='$FR':textfile='$(arq "$parcelas")':fontsize=42:fontcolor=white:x=(w-text_w)/2:y=$((1290+BLOCO_H+190)):enable='gte(t\,0.55)',"
  fc+="format=yuv420p[v]"
  "$FF" -hide_banner -loglevel error -y -loop 1 -t "$d" -i "$(win "${fs[0]}")" -loop 1 -t "$d" -i "$(win "${fs[0]}")" -filter_complex "$fc" -map '[v]' "${ENC[@]}" "$(win "$TMP/oferta.mp4")"
  segs+=("$TMP/oferta.mp4"); durs+=("$d")
fi

d=3.0; bloco "$cta" 20 66 white 1010 0.25; hc=$BLOCO_H
fc="color=c=${NAVY}:s=1080x1920:d=${d}:r=30[bg];[0:v]crop=iw:ih*0.74:0:0,scale=760:-2,format=rgba,fade=t=in:st=0:d=0.4:alpha=1[lg];[bg][lg]overlay=x=(W-w)/2:y=520[v1];"
fc+="[v1]drawbox=x=0:y=0:w=1080:h=10:color=${OURO}:t=fill,${BLOCO_F},"
fc+="$(anim "$FH" 'infinityguard.com.br' 60 "$OURO" $((1010+hc+50)) 0.45),"
fc+="$(anim "$FR" 'Link do produto na descrição' 44 white $((1010+hc+140)) 0.6),"
fc+="$(anim "$FR" 'Segurança para quem você ama' 38 0x9AA7B8 $((1010+hc+210)) 0.7),format=yuv420p[v]"
"$FF" -hide_banner -loglevel error -y -loop 1 -t "$d" -i "$(win "$LOGO")" -filter_complex "$fc" -map '[v]' "${ENC[@]}" "$(win "$TMP/fim.mp4")"
segs+=("$TMP/fim.mp4"); durs+=("$d")

x=0.3; trans=(smoothup slideleft smoothup slideleft smoothup slideleft smoothup slideleft)
ins=(); for s in "${segs[@]}"; do ins+=(-i "$(win "$s")"); done
total=$(printf '%s\n' "${durs[@]}" | awk -v x=$x -v n=${#segs[@]} '{s+=$1} END{printf "%.2f", s-x*(n-1)}')
chain=""; prev="[0:v]"; off=0
for ((k=1;k<${#segs[@]};k++)); do
  off=$(awk "BEGIN{printf \"%.2f\", $off+${durs[$((k-1))]}-$x}")
  chain+="${prev}[${k}:v]xfade=transition=${trans[$((k-1))]}:duration=${x}:offset=${off}[x$k];"; prev="[x$k]"
done
chain+="${prev}drawbox=x=0:y=0:w='1080*t/${total}':h=8:color=${OURO}:t=fill,format=yuv420p[v]"
ia=${#segs[@]}
if [ -f "$AQUI/acervo/marca/trilha.mp3" ]; then
  aud=(-i "$(win "$AQUI/acervo/marca/trilha.mp3")"); afc=";[${ia}:a]volume=0.22,afade=t=in:d=0.5,afade=t=out:st=$(awk "BEGIN{print $total-1.2}"):d=1.2,atrim=0:${total}[a]"
else
  aud=(-f lavfi -t "$total" -i anullsrc=r=44100:cl=stereo); afc=";[${ia}:a]anull[a]"
fi
mkdir -p "$(dirname "$SAIDA")"
"$FF" -hide_banner -loglevel error -y "${ins[@]}" "${aud[@]}" -filter_complex "${chain}${afc}" -map '[v]' -map '[a]' "${ENC[@]}" -c:a aac -b:a 128k -shortest -movflags +faststart "$(win "$SAIDA")"
echo "OK $SAIDA"
