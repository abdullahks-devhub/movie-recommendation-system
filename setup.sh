mkdir -p ~/.streamlit/
#!/bin/bash

git lfs install
git lfs pull

echo "\
[server]\n\
port = $PORT\n\
enableCORS = false\n\
headless = true\n\
\n\
" > ~/.streamlit/config.toml