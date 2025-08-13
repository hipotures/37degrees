#!/usr/bin/env bash
set -euo pipefail

log(){ printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }

usage(){ echo "Użycie: $0 create | $0 complete LIST_KEY" >&2; exit 1; }

require_todoit(){
  if ! command -v todoit >/dev/null 2>&1; then
    echo "Błąd: nie znaleziono polecenia 'todoit' w PATH." >&2
    exit 2
  fi
}

create_lists_and_items(){
  require_todoit
  log "Sprawdzam/zakładam tag 37d"
  todoit tag create 37d || true

  read -r -d '' KEYS <<'EOF'
0001_alice_in_wonderland
0002_animal_farm
0003_anna_karenina
0004_brave_new_world
0005_chlopi
0006_don_quixote
0007_dune
0019_master_and_margarita
0027_quo_vadis
0031_solaris
0036_treasure_island
EOF

  while IFS= read -r key; do
    [ -z "$key" ] && continue

    log "Lista: $key"
    if todoit list show "$key" >/dev/null 2>&1; then
      log "  istnieje"
    else
      log "  tworzę z tytułem"
      todoit list create "$key" --title "AI Image Generation for $key" || true
    fi

    log "  dodaję tag 37d"
    todoit list tag add "$key" 37d || true

    for i in $(seq 1 25); do
      printf -v n "%04d" "$i"
      item_key="item_${n}"
      item_content=$(printf "Generate image using scene_%02d.yaml" "$i")

      log "  pozycja: ${item_key}"
      if ! todoit item add "$key" "$item_key" "$item_content" >/dev/null 2>&1; then
        todoit item edit "$key" "$item_key" "$item_content" >/dev/null 2>&1 || true
      fi
      todoit item status "$key" "$item_key" --status completed
    done
  done <<<"$KEYS"

  log "Gotowe"
}

complete_1_to_25(){
  require_todoit
  local list_key=${1:-}
  [ -z "$list_key" ] && usage
  log "Ustawiam completed w: $list_key"
  for i in $(seq 1 25); do
    printf -v n "%04d" "$i"
    log "  item_${n} -> completed"
    todoit item status "$list_key" "item_${n}" --status completed
  done
  log "Gotowe"
}

case "${1:-}" in
  create)
    create_lists_and_items ;;
  complete)
    shift || true
    complete_1_to_25 "${1:-}" ;;
  *)
    usage ;;
esac

