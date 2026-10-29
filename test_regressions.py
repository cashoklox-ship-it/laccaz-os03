import os,sys,time,tempfile,subprocess,json
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import Qt,QProcess
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QMessageBox
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'config/includes.chroot/usr/share/laccaz'))
from appearance import Titlebar,STYLE
from devhub import Hub,Utility
from core import create_project
from tasks import plan
app=QApplication([]);app.setStyleSheet(STYLE)
def wait(predicate,timeout=15):
 deadline=time.monotonic()+timeout
 while not predicate() and time.monotonic()<deadline:app.processEvents();QTest.qWait(15)
 assert predicate(),'Timed out'
# Real mouse events to enlarged hit areas, not just invoking handlers.
w=QWidget();w.resize(650,400);v=QVBoxLayout(w);bar=Titlebar(w,'Window test');v.addWidget(bar);w.show();QTest.qWait(100)
assert all(b.size().width()==36 for b in bar.buttons.values())
QTest.mouseClick(bar.buttons['maximize'],Qt.LeftButton);QTest.qWait(100);assert w.isMaximized()
QTest.mouseClick(bar.buttons['maximize'],Qt.LeftButton);QTest.qWait(100);assert not w.isMaximized()
QTest.mouseClick(bar.buttons['minimize'],Qt.LeftButton);QTest.qWait(100);assert w.isMinimized();w.showNormal()
QTest.mouseClick(bar.buttons['close'],Qt.LeftButton);QTest.qWait(100);assert not w.isVisible()
print('PASS Qt close/minimize/maximize mouse clicks')
h=Hub();h.show()
with tempfile.TemporaryDirectory() as d:
 for lang in ['Python','C','C++','JavaScript']:
  root=create_project(d,lang.replace('+','p'),lang);h.current=root;h.run_sequence(plan(root,'run'))
  wait(lambda:h.proc is None and not h.pending)
  assert 'Hello from Laccaz OS!' in h.output.toPlainText(),h.output.toPlainText()
  assert 'Ошибка' not in h.state.text(),h.output.toPlainText()
 h.current=Path(d);h.output.clear();h.run_sequence([[sys.executable,'-c','import sys;sys.exit(3)'],[sys.executable,'-c','print("SHOULD_NOT_RUN")']]);wait(lambda:h.proc is None and not h.pending)
 assert 'SHOULD_NOT_RUN' not in h.output.toPlainText()
 h.run([sys.executable,'-c','import time;time.sleep(60)']);wait(lambda:h.proc is not None and h.proc.state()==QProcess.Running)
 with patch.object(QMessageBox,'question',return_value=QMessageBox.Yes):h.close()
 wait(lambda:h.proc is None);wait(lambda:not h.isVisible())
print('PASS all language task chains, fail-fast and close while process runs')
u=Utility();u.source.setPlainText('{"ok": true}');u.convert(lambda s:json.dumps(json.loads(s),indent=2));assert 'true' in u.result.toPlainText();assert json.loads(u.url_info('https://example.org/a?q=one&q=two'))['query']==[['q','one'],['q','two']]
print('PASS developer utility transformations')
