LIST_KEYS=(
  "au-local-de-context-specialist-research"
  "au-local-en-context-specialist-research"
  "au-local-es-context-specialist-research"
  "au-local-fr-context-specialist-research"
  "au-local-hi-context-specialist-research"
  "au-local-ja-context-specialist-research"
  "au-local-ko-context-specialist-research"
  "au-local-pt-context-specialist-research"
)

for key in "${LIST_KEYS[@]}"; do
  echo "Deleting list: $key"
  todoit list delete --force --list "$key"
done
