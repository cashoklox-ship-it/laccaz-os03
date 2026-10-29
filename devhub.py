#!/usr/bin/python3
"""Laccaz Dev Hub: local project tasks and developer utilities."""
import codecs
import hashlib
import json
import os
import shlex
import signal
import sys
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl
from PySide6.QtCore import Qt, QProcess, QTimer
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QLineEdit,QComboBox,QPlainTextEdit,QMessageBox,QFileDialog,QGroupBox,QListWidget,QListWidgetItem,QSizeGrip,QTabWidget,QInputDialog,QSplitter)
from appearance import STYLE, Titlebar
from core import create_project, TEMPLATES
from tasks import plan

class Hub(QMainWindow):
 def __init__(self):
  super().__init__();self.setWindowTitle('Laccaz Dev Hub');self.resize(1200,850);self.setMinimumSize(900,650);self.setWindowFlags(Qt.Window|Qt.FramelessWindowHint)
  self.current=Path.home();self.proc=None;self.pending=[];self.cancelled=False;self.close_pending=False
  w=QWidget();self.setCentralWidget(w);outer=QVBoxLayout(w);outer.setContentsMargins(16,8,16,8);self.titlebar=Titlebar(self,'Dev Hub');outer.addWidget(self.titlebar)
  split=QHBoxLayout();outer.addLayout(split,1)
  side=QWidget();side.setObjectName('sidebar');side.setFixedWidth(210);nav=QVBoxLayout(side);nav.setContentsMargins(16,22,16,20);split.addWidget(side)
  logo=QLabel('Dev Hub');logo.setObjectName('brand');nav.addWidget(logo);sub=QLabel('Твоё рабочее пространство');sub.setObjectName('muted');nav.addWidget(sub);nav.addSpacing(18)
  for label,fn in [('+ Новый проект',lambda:self.name.setFocus()),('Открыть папку…',self.choose),('Редактор кода',lambda:self.launch('kate',str(self.current))),('Терминал',lambda:self.launch('konsole','--workdir',str(self.current)))]:nav.addWidget(self.button(label,fn))
  nav.addWidget(QLabel('ПРОЕКТЫ'));self.recent=QListWidget();self.recent.itemClicked.connect(self.select_recent);nav.addWidget(self.recent,1);nav.addWidget(self.button('Обновить список',self.refresh_projects));self.refresh_projects()
  main=QWidget();v=QVBoxLayout(main);v.setContentsMargins(20,8,4,0);v.setSpacing(12);split.addWidget(main,1)
  title=QLabel('От идеи — к работающему коду.');title.setObjectName('hero');title.setWordWrap(True);v.addWidget(title)
  self.location=QLabel();self.location.setObjectName('muted');self.location.setWordWrap(True);v.addWidget(self.location)
  box=QGroupBox('Новый проект');row=QHBoxLayout(box);self.name=QLineEdit();self.name.setPlaceholderText('Название');row.addWidget(self.name,1);self.lang=QComboBox();self.lang.addItems(TEMPLATES);row.addWidget(self.lang);row.addWidget(self.button('Создать',self.create,True));v.addWidget(box)
  tabs=QTabWidget();v.addWidget(tabs);project=QWidget();row=QHBoxLayout(project)
  for label,task in [('▶ Запуск','run'),('Сборка','build'),('Тесты','test'),('Зависимости','deps')]:row.addWidget(self.button(label,lambda t=task:self.project_task(t)))
  row.addWidget(self.button('Python venv',lambda:self.run([sys.executable,'-m','venv','.venv'])));tabs.addTab(project,'Проект')
  git=QWidget();row=QHBoxLayout(git)
  for label,cmd in [('Статус',['git','status','--short','--branch']),('Изменения',['git','diff']),('История',['git','log','-12','--oneline','--decorate']),('Git init',['git','init'])]:row.addWidget(self.button(label,lambda c=cmd:self.run(c)))
  row.addWidget(self.button('В индекс…',self.stage_all));row.addWidget(self.button('Коммит…',self.commit));tabs.addTab(git,'Git')
  tools=QWidget();row=QHBoxLayout(tools)
  for label,cmd in [('Инструменты',['laccaz-doctor']),('Docker',['docker','ps','-a']),('CMake',['cmake','--version']),('Порты',['ss','-lnt'])]:row.addWidget(self.button(label,lambda c=cmd:self.run(c)))
  row.addWidget(self.button('JSON / URL / SHA-256',self.utilities));tabs.addTab(tools,'Инструменты')
  self.state=QLabel('Готов к работе');self.state.setObjectName('muted');v.addWidget(self.state)
  self.output=QPlainTextEdit();self.output.setReadOnly(True);self.output.setMaximumBlockCount(6000);self.output.setPlaceholderText('Вывод команд появится здесь.');v.addWidget(self.output,1)
  row=QHBoxLayout();self.command=QLineEdit();self.command.setPlaceholderText('Команда: python3 main.py');self.command.returnPressed.connect(self.custom);row.addWidget(self.command,1);row.addWidget(self.button('Запустить',self.custom,True));row.addWidget(self.button('Стоп',self.stop));v.addLayout(row)
  row=QHBoxLayout();row.addWidget(self.button('Файлы',lambda:self.launch('dolphin',str(self.current))));row.addWidget(self.button('Сохранить лог',self.save_log));row.addWidget(self.button('Очистить',self.output.clear));row.addStretch();row.addWidget(QSizeGrip(self));v.addLayout(row);self.update_path()
 def button(self,label,fn,primary=False):
  b=QPushButton(label);b.clicked.connect(lambda checked=False:fn())
  if primary:b.setObjectName('primary')
  return b
 def refresh_projects(self):
  self.recent.clear();root=Path.home()/'Projects'
  if root.exists():
   for p in sorted(root.iterdir()):
    if p.is_dir():it=QListWidgetItem(p.name);it.setData(Qt.UserRole,str(p));self.recent.addItem(it)
 def select_recent(self,it):self.current=Path(it.data(Qt.UserRole));self.update_path()
 def update_path(self):self.location.setText(str(self.current))
 def choose(self):
  d=QFileDialog.getExistingDirectory(self,'Открыть проект',str(Path.home()/'Projects'))
  if d:self.current=Path(d);self.update_path()
 def create(self):
  try:self.current=create_project(Path.home()/'Projects',self.name.text().strip(),self.lang.currentText());self.update_path();self.refresh_projects();self.output.appendPlainText('Создан: '+str(self.current))
  except Exception as e:QMessageBox.warning(self,'Проект',str(e))
 def launch(self,program,*args):
  result=QProcess.startDetached(program,list(args))
  if not (result[0] if isinstance(result,tuple) else result):QMessageBox.warning(self,'Запуск','Не удалось открыть '+program)
 def custom(self):
  try:cmd=shlex.split(self.command.text())
  except ValueError as e:QMessageBox.warning(self,'Команда',str(e));return
  if cmd:self.run(cmd)
 def project_task(self,task):
  try:self.run_sequence(plan(self.current,task))
  except ValueError as e:QMessageBox.information(self,'Задача',str(e))
 def run(self,cmd):self.run_sequence([cmd])
 def run_sequence(self,commands):
  if self.proc is not None or self.pending:QMessageBox.information(self,'Процесс','Сначала дождись завершения или нажми Стоп.');return
  self.pending=[list(c) for c in commands];self.task_dir=str(self.current);self.cancelled=False;self.next_command()
 def next_command(self):
  if not self.pending:return
  cmd=self.pending.pop(0);self.output.appendPlainText('\n$ '+shlex.join(cmd)+'\n');self.state.setText('Выполняется: '+cmd[0]);p=QProcess(self);self.proc=p;self.decoder=codecs.getincrementaldecoder('utf-8')(errors='replace');p.setWorkingDirectory(self.task_dir);p.setProcessChannelMode(QProcess.MergedChannels)
  p.readyReadStandardOutput.connect(lambda:self.read_output(p));p.finished.connect(lambda code,status:self.done(p,code));p.errorOccurred.connect(lambda error:self.failed(p,error))
  # A new POSIX session lets Stop terminate compilers and their children as well.
  if sys.platform.startswith('linux'):p.start('setsid',cmd)
  else:p.start(cmd[0],cmd[1:])
 def read_output(self,p):
  chunk=self.decoder.decode(bytes(p.readAllStandardOutput()))
  if chunk:self.output.moveCursor(self.output.textCursor().MoveOperation.End);self.output.insertPlainText(chunk);self.output.ensureCursorVisible()
 def failed(self,p,error):
  if error==QProcess.FailedToStart:self.output.appendPlainText(p.errorString());self.pending.clear();self.proc=None;p.deleteLater();self.state.setText('Не удалось запустить команду');self.finish_close()
 def done(self,p,code):
  self.read_output(p);tail=self.decoder.decode(b'',final=True)
  if tail:self.output.insertPlainText(tail)
  self.output.appendPlainText('\nКод завершения: '+str(code));self.proc=None;p.deleteLater()
  if code!=0 or self.cancelled:self.pending.clear()
  self.state.setText('Остановлено' if self.cancelled else ('Готово' if code==0 else 'Ошибка — смотри вывод'))
  if self.pending:QTimer.singleShot(0,self.next_command)
  else:self.finish_close()
 def signal_process(self,p,sig):
  if self.proc is not p:return
  pid=int(p.processId())
  if pid<=0:return
  try:
   if os.getpgid(pid)==pid:os.killpg(pid,sig)
   else:p.kill() if sig==signal.SIGKILL else p.terminate()
  except (ProcessLookupError,PermissionError):p.kill() if sig==signal.SIGKILL else p.terminate()
 def stop(self):
  self.cancelled=True;self.pending.clear()
  if self.proc:
   p=self.proc;self.signal_process(p,signal.SIGTERM);QTimer.singleShot(2000,lambda:self.signal_process(p,signal.SIGKILL))
 def finish_close(self):
  if self.close_pending:QTimer.singleShot(0,self.close)
 def closeEvent(self,event):
  if self.proc or self.pending:
   if QMessageBox.question(self,'Закрыть Dev Hub?','Остановить выполняемую задачу и закрыть окно?')==QMessageBox.Yes:self.close_pending=True;self.stop();event.ignore()
   else:event.ignore()
  else:event.accept()
 def stage_all(self):
  if QMessageBox.question(self,'Индекс Git','Добавить ВСЕ изменения текущего проекта в индекс Git?')==QMessageBox.Yes:self.run(['git','add','--all'])
 def commit(self):
  msg,ok=QInputDialog.getText(self,'Коммит Git','Сообщение коммита (только уже добавленные изменения):')
  if ok and msg.strip():self.run(['git','commit','-m',msg.strip()])
 def save_log(self):
  path,_=QFileDialog.getSaveFileName(self,'Сохранить лог','devhub.log','Log (*.log);;Text (*.txt)')
  if path:
   try:Path(path).write_text(self.output.toPlainText())
   except OSError as e:QMessageBox.warning(self,'Лог',str(e))
 def utilities(self):
  if not hasattr(self,'utility'):
   self.utility=Utility(self)
  self.utility.show();self.utility.raise_();self.utility.activateWindow()

class Utility(QWidget):
 def __init__(self,parent=None):
  super().__init__(parent,Qt.Window|Qt.FramelessWindowHint);self.setWindowTitle('Laccaz Developer Tools');self.resize(820,620);v=QVBoxLayout(self);v.addWidget(Titlebar(self,'Developer Tools'));v.addWidget(QLabel('JSON · URL · SHA-256'));self.source=QPlainTextEdit();self.source.setPlaceholderText('Вставь JSON, URL или текст');v.addWidget(self.source,1);row=QHBoxLayout();v.addLayout(row)
  for label,fn in [('Формат JSON',lambda s:json.dumps(json.loads(s),ensure_ascii=False,indent=2)),('Разобрать URL',self.url_info),('SHA-256 текста',lambda s:hashlib.sha256(s.encode()).hexdigest())]:
   b=QPushButton(label);b.clicked.connect(lambda checked=False,transform=fn:self.convert(transform));row.addWidget(b)
  self.result=QPlainTextEdit();self.result.setReadOnly(True);v.addWidget(self.result,1);row=QHBoxLayout();v.addLayout(row);b=QPushButton('Скопировать результат');b.clicked.connect(lambda:QApplication.clipboard().setText(self.result.toPlainText()));row.addWidget(b);row.addStretch();row.addWidget(QSizeGrip(self))
 def url_info(self,s):
  u=urlsplit(s.strip());return json.dumps({'scheme':u.scheme,'host':u.hostname,'port':u.port,'path':u.path,'query':parse_qsl(u.query,keep_blank_values=True),'fragment':u.fragment},ensure_ascii=False,indent=2)
 def convert(self,fn):
  try:self.result.setPlainText(fn(self.source.toPlainText()))
  except Exception as e:self.result.setPlainText('Ошибка: '+str(e))

if __name__=='__main__':
 app=QApplication(sys.argv);app.setStyle('Fusion');app.setStyleSheet(STYLE);h=Hub();h.show();sys.exit(app.exec())
