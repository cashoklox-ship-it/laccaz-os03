"""Project task plans; no shell interpolation."""
from pathlib import Path
import json,sys

def language(root):
 root=Path(root)
 if (root/'CMakeLists.txt').exists() or (root/'main.cpp').exists():return 'C++'
 if (root/'main.c').exists():return 'C'
 if (root/'package.json').exists():return 'JavaScript'
 if (root/'main.py').exists():return 'Python'
 raise ValueError('Не найден main.py, main.c, main.cpp или package.json.')

def python(root):
 venv=Path(root)/'.venv/bin/python'
 return str(venv) if venv.exists() else sys.executable

def plan(root,task):
 root=Path(root);lang=language(root)
 if task=='build':
  if lang=='C':return [['gcc','-std=c17','-Wall','-Wextra','-g','main.c','-o','app']]
  if lang=='C++':return [['cmake','-S','.','-B','build','-DCMAKE_BUILD_TYPE=Debug'],['cmake','--build','build','--parallel','2']]
  if lang=='Python':return [[python(root),'-m','py_compile','main.py']]
  return [['node','--check','main.js']]
 if task=='run':
  if lang=='Python':return [[python(root),'main.py']]
  if lang=='JavaScript':return [['npm','start']]
  return plan(root,'build')+[[str(root/('build/app' if lang=='C++' else 'app'))]]
 if task=='test':
  if lang=='Python':return [[python(root),'-m','pytest','-q']]
  if lang=='JavaScript':return [['npm','test']]
  if lang=='C++':return plan(root,'build')+[['ctest','--test-dir','build','--output-on-failure','--no-tests=error']]
  raise ValueError('Для C добавь тесты и запускай свою команду в консоли.')
 if task=='deps':
  if lang=='Python':
   if not (root/'requirements.txt').is_file():raise ValueError('В проекте нет requirements.txt.')
   if not (root/'.venv/bin/python').exists():return [[sys.executable,'-m','venv','.venv'],[str(root/'.venv/bin/python'),'-m','pip','install','-r','requirements.txt']]
   return [[python(root),'-m','pip','install','-r','requirements.txt']]
  if lang=='JavaScript':return [['npm','ci' if (root/'package-lock.json').exists() else 'install']]
  raise ValueError('Зависимости C/C++ задаются проектом. Здесь автоматическая установка не настроена.')
 raise ValueError('Неизвестная задача')
