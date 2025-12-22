#!/bin/bash

for file in $(git ls-files | grep DECK.md); do
  yaml_file="${file%.md}.yaml"
  if [ -f "$yaml_file" ]; then
    title=$(grep -m 1 "^>###.*" "$file" | sed -e 's/^>###//; s/ .*//')
    if [ -z "$title" ]; then
      title=$(grep -m 1 "^##.*" "$file" | sed -e 's/^##//; s/ .*//')
    fi
    if [ -z "$title" ]; then
      title=$(grep -m 1 "^#.*" "$file" | sed -e 's/^#//; s/ .*//')
    fi
    prefix=$(grep -m 1 "prefix:" "$yaml_file" | sed -e 's/prefix://; s/ //g')
    status=$(grep -m 1 "status:" "$yaml_file" | sed -e 's/status://; s/ //g')
    case $status in
      NOT\ STARTED)
        color="lightgrey"
        ;;
      ONGOING)
        color="yellow"
        ;;
      DONE)
        color="brightgreen"
        ;;
      *)
        color="gray"
        ;;
    esac
    title_line="$prefix $title"
    echo "$title_line ![status](https://img.shields.io/badge/status-$status-$color)
<details $(if [ \"$status\" = \"ONGOING\" ]; then echo \"open\"; fi)>
  <summary>Details</summary>
  <!-- your content here -->
</details>" > temp.md
    cat temp.md > "$file"
    rm temp.md
  fi
done
