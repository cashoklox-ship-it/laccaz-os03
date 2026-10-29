import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QMimeData
from PySide6.QtGui import QPainter
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'config/includes.chroot/usr/share/laccaz'))
from shell import Shell,STYLE
app=QApplication([]);app.setStyle('Fusion');app.setStyleSheet(STYLE)
s=Shell(preview=True);s.root.resize(1440,900);s.bar.resize(1440,38)
cb=app.clipboard();cb.setText('print("Hello, Laccaz")');assert s.history==['print("Hello, Laccaz")']
cb.setText('cmake --build build');assert len(s.history)==2
cb.setText('print("Hello, Laccaz")');assert len(s.history)==2
s.pause.setChecked(True);cb.setText('not-recorded');assert 'not-recorded' not in s.history;s.pause.setChecked(False)
m=QMimeData();m.setText('sensitive');m.setData('x-kde-passwordManagerHint',b'secret');cb.setMimeData(m);assert 'sensitive' not in s.history
s.show('clips');assert s.list.count()==2;s.activate(s.list.item(1));assert cb.text()=='cmake --build build'
s.show('clips');s.clear();assert not s.history and not cb.text()
for i in range(45):cb.setText('snippet '+str(i))
assert len(s.history)==40
s.search.setText('snippet 44');assert s.list.count()==1
s.show('files');assert s.list.count()>0
s.clear();s.drawer.hide()
preview=r/'previews';preview.mkdir(exist_ok=True);app.processEvents()
im=s.root.grab();p=QPainter(im);p.drawPixmap((1440-s.panel.width())//2,900-s.panel.height()-14,s.panel.grab());p.drawPixmap(0,0,s.bar.grab());p.end();im.save(str(preview/'surface-desktop.png'))
cb.setText('git status --short');cb.setText('python3 -m venv .venv');s.show('clips');app.processEvents();s.drawer.grab().save(str(preview/'surface-clipboard.png'))
print('PASS clipboard capture, dedup, pause, sensitive MIME, restore, clear, cap, search, files and widget startup')
