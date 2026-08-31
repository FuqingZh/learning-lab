#!/usr/bin/env bash

set -euo pipefail

readonly -a TRACKS=(
  "bioinformatics-systems"
  "scientific-ai-platforms"
)

is_known_track() {
  local candidate=$1
  local track

  for track in "${TRACKS[@]}"; do
    if [[ "${candidate}" == "${track}" ]]; then
      return 0
    fi
  done
  return 1
}

for path in \
  README.md \
  package.json \
  package-lock.json \
  AGENTS.md \
  MISSION.md \
  CURRICULUM.md \
  RESOURCES.md \
  NOTES.md \
  GLOSSARY.md \
  docs/README.md \
  docs/implementation-plans/20260820-v1.0-knowledge-map-implementation-plan.md \
  docs/implementation-plans/20260821-v1.1-ambient-learning-implementation-plan.md \
  docs/implementation-plans/20260824-v1.2-evidence-backed-knowledge-history-plan.md \
  docs/implementation-plans/20260824-v1.3-typescript-explorer-and-evidence-graph-plan.md \
  docs/how-to-guides/20260824-v1.2-add-evidence-backed-history-how-to-guide.md \
  frontend/README.md \
  .agents/skills/learning-lab-tutor/SKILL.md \
  histories/README.md \
  learning-state/README.md \
  learning-records/README.md \
  lessons/README.md \
  maps/README.md \
  site/index.html
do
  if [[ ! -f "${path}" ]]; then
    echo "missing required workspace entrypoint: ${path}" >&2
    exit 1
  fi
done

for track in "${TRACKS[@]}"; do
  for path in \
    "tracks/${track}/README.md" \
    "tracks/${track}/CURRICULUM.md" \
    "tracks/${track}/RESOURCES.md" \
    "learning-records/${track}"
  do
    if [[ ! -e "${path}" ]]; then
      echo "missing track boundary: ${path}" >&2
      exit 1
    fi
  done
done

if [[ ! -f "tracks/bioinformatics-systems/SYSTEMS-MAP.md" ]]; then
  echo "missing required systems-map entrypoint: tracks/bioinformatics-systems/SYSTEMS-MAP.md" >&2
  exit 1
fi

for root in tracks learning-records lessons; do
  while IFS= read -r directory; do
    track=${directory##*/}
    if ! is_known_track "${track}"; then
      echo "unknown track directory: ${directory}" >&2
      exit 1
    fi
  done < <(find "${root}" -mindepth 1 -maxdepth 1 -type d -print)
done

mapfile -t flat_records < <(
  find learning-records -mindepth 1 -maxdepth 1 -type f ! -name README.md -print
)
if ((${#flat_records[@]})); then
  echo "learning records must be placed under a track:" >&2
  printf '  %s\n' "${flat_records[@]}" >&2
  exit 1
fi

mapfile -t flat_lessons < <(
  find lessons -mindepth 1 -maxdepth 1 -type f ! -name README.md -print
)
if ((${#flat_lessons[@]})); then
  echo "lessons must be placed under a track:" >&2
  printf '  %s\n' "${flat_lessons[@]}" >&2
  exit 1
fi

mapfile -t numbered_lessons < <(
  find lessons -mindepth 2 -type f -printf '%p\n' \
    | awk -F/ '$NF ~ /^[0-9][0-9][0-9][0-9]-/'
)
if ((${#numbered_lessons[@]})); then
  echo "lesson filenames must use semantic topics, not global numbers:" >&2
  printf '  %s\n' "${numbered_lessons[@]}" >&2
  exit 1
fi

python3 scripts/build-knowledge-map.py validate
python3 scripts/build-learning-state.py validate
python3 scripts/build-learning-records.py validate
python3 scripts/build-knowledge-history.py validate
python3 scripts/check-teaching-navigation.py validate
npm run frontend:verify
python3 tests/knowledge-map/test_validation.py
python3 tests/knowledge-map/test_markdown_render.py
python3 tests/knowledge-map/test_site_render.py
python3 tests/knowledge-map/test_frontend_contract.py
python3 tests/knowledge-history/test_validation.py
python3 tests/learning-state/test_learning_state.py
python3 tests/learning-records/test_learning_records.py
python3 tests/learning-skill/test_learning_lab_tutor.py
python3 tests/learning-skill/test_teaching_navigation.py
python3 scripts/run-tutor-evaluation.py verify-static
python3 tests/learning-skill/test_tutor_evaluation_contract.py
python3 scripts/check-knowledge-map-generated.py

echo "learning-lab structure: ok"
