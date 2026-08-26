import os
import glob

for f in glob.glob('src/**/*.tsx', recursive=True):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace("import React from 'react';\n", '')
    content = content.replace("import React, ", "import ")
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
