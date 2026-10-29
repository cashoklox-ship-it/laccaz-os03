from pathlib import Path
import re, subprocess, sys
TEMPLATES = {
 'Python': {'main.py': 'print("Hello from Laccaz OS!")\n', '.gitignore': '.venv/\n__pycache__/\n'},
 'C': {'main.c': '#include <stdio.h>\nint main(void) { puts("Hello from Laccaz OS!"); return 0; }\n', 'Makefile': 'app: main.c\n\t$(CC) -Wall -Wextra -g main.c -o app\n', '.gitignore': 'app\n'},
 'C++': {'main.cpp': '#include <iostream>\nint main() { std::cout << "Hello from Laccaz OS!\\n"; }\n', 'CMakeLists.txt': 'cmake_minimum_required(VERSION 3.20)\nproject(laccaz_app LANGUAGES CXX)\nset(CMAKE_CXX_STANDARD 20)\nadd_executable(app main.cpp)\n', '.gitignore': 'build/\n'},
 'JavaScript': {'main.js': 'console.log("Hello from Laccaz OS!");\n', 'package.json': '{"name":"laccaz-app","private":true,"scripts":{"start":"node main.js"}}\n', '.gitignore': 'node_modules/\n'}
}
def create_project(root, name, language):
 if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', name):
  raise ValueError('Имя: латинские буквы, цифры, дефис или _, до 64 символов.')
 if language not in TEMPLATES: raise ValueError('Unknown language')
 root=Path(root).expanduser();root.mkdir(parents=True,exist_ok=True)
 target=root/name;target.mkdir()  # never overwrite an existing project
 for filename, content in TEMPLATES[language].items(): (target/filename).write_text(content)
 (target/'README.md').write_text(f'# {name}\n\nCreated with Laccaz OS Dev Hub.\n')
 return target
