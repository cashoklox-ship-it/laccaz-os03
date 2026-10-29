#!/usr/bin/python3
import json,shutil,sys
from pathlib import Path
from PySide6.QtCore import Qt,QProcess,QTimer,QSize
from PySide6.QtGui import QIcon,QPixmap,QPainter,QColor,QFont
from PySide6.QtWidgets import QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QLineEdit,QListWidget,QListWidgetItem,QPlainTextEdit,QMessageBox,QSizeGrip,QSplitter,QProgressBar
from appearance import STYLE,Titlebar
CATALOG=Path(__file__).with_name('catalog.json')
class AppCenter(QMainWindow):
 def __init__(self,backend='pkexec'):
  super().__init__();self.backend=backend;self.catalog=json.loads(CATALOG.read_text());self.installed=set();self.status_ready=False;self.last_result='';self.proc=None;self.check=None;self.category='Все';self.setWindowTitle('Laccaz App Center');self.resize(1120,790);self.setMinimumSize(920,650);self.setWindowFlags(Qt.Window|Qt.FramelessWindowHint)
  root=QWidget();self.setCentralWidget(root);v=QVBoxLayout(root);v.setContentsMargins(16,8,16,12);v.addWidget(Titlebar(self,'Центр приложений'));row=QHBoxLayout();v.addLayout(row,1)
  sidebar=QWidget();sidebar.setObjectName('sidebar');sidebar.setFixedWidth(205);nav=QVBoxLayout(sidebar);nav.setContentsMargins(16,22,16,18);label=QLabel('Приложения');label.setObjectName('brand');nav.addWidget(label);nav.addWidget(QLabel('Для твоей Laccaz OS'));nav.addSpacing(22)
  for name in ['Все','Установленные']+sorted({a['category'] for a in self.catalog}):
   b=QPushButton(name);b.clicked.connect(lambda checked=False,n=name:self.filter_category(n));nav.addWidget(b)
  nav.addStretch();b=QPushButton('Обновить каталог');b.clicked.connect(lambda:self.transaction('refresh'));nav.addWidget(b);row.addWidget(sidebar)
  main=QWidget();body=QVBoxLayout(main);body.setContentsMargins(20,8,4,0);row.addWidget(main,1);hero=QLabel('Найди своё следующее приложение.');hero.setObjectName('hero');hero.setWordWrap(True);body.addWidget(hero);sub=QLabel('Подборка программ из подключённых репозиториев Debian');sub.setObjectName('muted');body.addWidget(sub)
  self.search=QLineEdit();self.search.setPlaceholderText('Название, категория или описание');self.search.textChanged.connect(self.populate);body.addWidget(self.search)
  split=QSplitter();self.list=QListWidget();self.list.setIconSize(QSize(42,42));self.list.currentItemChanged.connect(self.select);split.addWidget(self.list);details=QWidget();detail=QVBoxLayout(details);self.name=QLabel('Выбери приложение');self.name.setObjectName('brand');self.name.setWordWrap(True);detail.addWidget(self.name);self.description=QLabel();self.description.setWordWrap(True);detail.addWidget(self.description);self.package=QLabel();self.package.setObjectName('muted');self.package.setWordWrap(True);detail.addWidget(self.package);detail.addStretch();self.action=QPushButton('Установить');self.action.setObjectName('primary');self.action.clicked.connect(self.install_or_remove);self.action.setEnabled(False);detail.addWidget(self.action);self.open=QPushButton('Открыть');self.open.clicked.connect(self.launch);self.open.setEnabled(False);detail.addWidget(self.open);split.addWidget(details);split.setSizes([400,300]);body.addWidget(split,1)
  self.progress=QProgressBar();self.progress.setRange(0,0);self.progress.hide();body.addWidget(self.progress);self.status=QLabel('Проверка установленных пакетов…');self.status.setWordWrap(True);body.addWidget(self.status)
  self.log=QPlainTextEdit();self.log.setReadOnly(True);self.log.setMaximumBlockCount(3000);self.log.setMaximumHeight(145);self.log.setPlaceholderText('Здесь будет вывод установки.');body.addWidget(self.log);self.log.hide();foot=QHBoxLayout();foot.addWidget(QLabel('Live: приложения могут исчезнуть после перезагрузки.' if Path('/run/live/medium').exists() else 'Установка требует интернета и разрешения администратора.'));foot.addStretch();foot.addWidget(QSizeGrip(self));body.addLayout(foot)
  self.populate();QTimer.singleShot(0,self.refresh_status)
 def filter_category(self,name):self.category=name;self.populate()
 def populate(self):
  selected=self.selected()['package'] if self.selected() else None;self.list.clear();q=self.search.text().casefold()
  for a in self.catalog:
   if self.category=='Установленные' and a['package'] not in self.installed:continue
   if self.category not in ('Все','Установленные',a['category']):continue
   if q and q not in (' '.join([a['name'],a['summary'],a['package'],a['category']])).casefold():continue
   text=a['name']+'\n'+a['summary']+('  ·  Установлено' if a['package'] in self.installed else '');icon=QIcon.fromTheme(a['exec'])
   if icon.isNull():
    pix=QPixmap(44,44);pix.fill(Qt.transparent);p=QPainter(pix);p.setRenderHint(QPainter.Antialiasing);p.setBrush(QColor(['#4a8cf5','#8e65d9','#36a99d','#e68b4d'][len(a['name'])%4]));p.setPen(Qt.NoPen);p.drawRoundedRect(0,0,44,44,11,11);p.setPen(QColor('white'));p.setFont(QFont('DejaVu Sans',17,QFont.Bold));p.drawText(pix.rect(),Qt.AlignCenter,a['name'][0]);p.end();icon=QIcon(pix)
   it=QListWidgetItem(icon,text);it.setData(Qt.UserRole,a);self.list.addItem(it)
   if a['package']==selected:self.list.setCurrentItem(it)
  if self.list.currentRow()<0 and self.list.count():self.list.setCurrentRow(0)
  self.select()
 def selected(self):
  it=self.list.currentItem();return it.data(Qt.UserRole) if it else None
 def select(self,*args):
  a=self.selected();busy=self.proc is not None
  if not a:self.name.setText('Нет приложений');self.description.clear();self.package.clear();self.action.setEnabled(False);self.open.setEnabled(False);return
  self.name.setText(a['name']);self.description.setText(a['summary']);self.package.setText('Пакет: '+a['package']+'\n'+a['category']);installed=a['package'] in self.installed;self.action.setText('Удалить' if installed else 'Установить');self.action.setEnabled(self.status_ready and not busy);self.open.setEnabled(installed and not busy)
 def refresh_status(self):
  if self.check:return
  p=QProcess(self);self.check=p;p.finished.connect(lambda code,state:self.status_result(p,code));p.errorOccurred.connect(lambda e:self.status_error(p,e));p.start('dpkg-query',['-W','-f=${binary:Package} ${db:Status-Status}\n'])
 def status_error(self,p,error):
  if error==QProcess.FailedToStart:self.check=None;self.status_ready=False;self.status.setText('Не удалось запустить dpkg-query.');self.select();p.deleteLater()
 def status_result(self,p,code):
  self.installed={line.split()[0].split(':')[0] for line in bytes(p.readAllStandardOutput()).decode(errors='replace').splitlines() if len(line.split())==2 and line.split()[1]=='installed'};self.status_ready=code==0;self.check=None;p.deleteLater();self.populate()
  if self.proc is None:self.status.setText(self.last_result or ('Готово. '+str(len(self.catalog))+' приложений в подборке.' if code==0 else 'Не удалось проверить установленные пакеты.'))
 def install_or_remove(self):
  a=self.selected()
  if a:self.transaction('remove' if a['package'] in self.installed else 'install',a['package'])
 def transaction(self,action,package=None):
  if self.proc:return
  if self.backend!='pkexec':self.status.setText('Тестовый режим: установка отключена.');return
  verb={'install':'Установить','remove':'Удалить','refresh':'Обновить индексы пакетов'}[action]
  if QMessageBox.question(self,'Центр приложений',verb+(' '+package if package else '')+'?\nЗапрос разрешения появится в системном окне.')!=QMessageBox.Yes:return
  p=QProcess(self);self.proc=p;self.log.clear();self.log.show();self.progress.show();self.status.setText('Ожидание разрешения / выполнение операции…');self.select();p.setProcessChannelMode(QProcess.MergedChannels);p.readyReadStandardOutput.connect(lambda:self.log.appendPlainText(bytes(p.readAllStandardOutput()).decode(errors='replace').rstrip()));p.finished.connect(lambda code,state:self.finished(p,code));p.errorOccurred.connect(lambda e:self.failed(p,e));args=['--disable-internal-agent','/usr/libexec/laccaz-package-action',action]+([package] if package else []);p.start('pkexec',args)
 def failed(self,p,error):
  if error==QProcess.FailedToStart:self.proc=None;self.progress.hide();self.status.setText('Не найден pkexec. Установи pkexec и агент polkit.');self.select();p.deleteLater()
 def finished(self,p,code):
  self.log.appendPlainText(bytes(p.readAllStandardOutput()).decode(errors='replace'));self.proc=None;self.progress.hide();p.deleteLater();self.last_result='Операция завершена.' if code==0 else ('Разрешение отменено или не получено.' if code in (126,127) else 'Ошибка. Проверь интернет и журнал ниже.');self.status.setText(self.last_result);self.refresh_status();self.select()
 def launch(self):
  a=self.selected()
  if not a:return
  exe=a['exec'];args=[]
  if exe=='htop':exe='konsole';args=['-e','htop']
  result=QProcess.startDetached(exe,args)
  if not (result[0] if isinstance(result,tuple) else result):QMessageBox.warning(self,'Запуск','Приложение не запустилось. Проверь установку пакета.')
 def closeEvent(self,event):
  if self.proc:QMessageBox.information(self,'Установка','Дождись завершения операции с пакетами.');event.ignore()
  else:event.accept()
if __name__=='__main__':
 app=QApplication(sys.argv);app.setStyle('Fusion');app.setStyleSheet(STYLE);w=AppCenter();w.show();sys.exit(app.exec())
