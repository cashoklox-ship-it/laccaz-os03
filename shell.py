#!/usr/bin/python3
import configparser, os, shutil, sys
from pathlib import Path
from PySide6.QtCore import Qt,QTimer,QProcess,QDateTime,QUrl,QSize,QSocketNotifier,QSettings,QLocale,QDate,QPoint,QRectF
from PySide6.QtGui import QPainter,QColor,QPen,QFont,QDesktopServices,QLinearGradient,QPainterPath,QRegion,QPixmap,QImage
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QLineEdit,QListWidget,QListWidgetItem,QStackedWidget,QMessageBox,QCheckBox,QFrame,QSizePolicy,QCalendarWidget,QFileDialog
from appearance import STYLE, Titlebar, dock_icon,DockButton

def start(program,args=[]):
 ok=QProcess.startDetached(program,args)
 return ok[0] if isinstance(ok,tuple) else ok

def applications():
 found={}
 roots=[Path.home()/'.local/share/applications',Path('/usr/local/share/applications'),Path('/usr/share/applications')]
 seen=set()
 for root in roots:
  for p in sorted(root.glob('**/*.desktop')):
   desktop_id=str(p.relative_to(root)).replace('/','-')
   if desktop_id in seen:continue
   seen.add(desktop_id)
   try:
    c=configparser.ConfigParser(interpolation=None,strict=False);c.read(p);e=c['Desktop Entry']
    if e.get('Type')!='Application' or e.get('NoDisplay','false')=='true' or e.get('Hidden','false')=='true':continue
    if 'OnlyShowIn' in e and not any(x in ('Laccaz','KDE') for x in e['OnlyShowIn'].split(';')):continue
    if 'Laccaz' in e.get('NotShowIn','').split(';'):continue
    if e.get('TryExec') and not shutil.which(e['TryExec']):continue
    name=e.get('Name[ru]',e.get('Name',p.stem));found[desktop_id]=(name,str(p))
   except Exception:continue
 return sorted(found.values(),key=lambda x:x[0].casefold())
class GlassPanel(QFrame):
 def __init__(self,backdrop,parent=None):
  super().__init__(parent);self.backdrop=backdrop;self.setAttribute(Qt.WA_TranslucentBackground)
 def paintEvent(self,event):
  p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);path=QPainterPath();path.addRoundedRect(QRectF(self.rect()).adjusted(1,1,-1,-1),22,22);p.setClipPath(path)
  origin=self.backdrop.mapFromGlobal(self.mapToGlobal(QPoint(0,0)));p.drawPixmap(self.rect(),self.backdrop.blurred(),self.rect().translated(origin));p.fillPath(path,QColor(248,251,255,150));p.setClipping(False);p.setPen(QPen(QColor(255,255,255,180),1));p.drawPath(path);p.end()
class Dock(GlassPanel):
 def resizeEvent(self,event):
  path=QPainterPath();path.addRoundedRect(QRectF(self.rect()),23,23);self.setMask(QRegion(path.toFillPolygon().toPolygon()));super().resizeEvent(event)
class Backdrop(QWidget):
 def __init__(self):
  super().__init__();self.settings=QSettings('Laccaz','Desktop');self.image=QPixmap();self.cached=None;self.blur_cache=None;self.load_wallpaper(self.settings.value('wallpaper',str(Path(__file__).with_name('coast-wallpaper.png'))))
 def load_wallpaper(self,path):
  image=QPixmap(path)
  if image.isNull():image=QPixmap(str(Path(__file__).with_name('coast-wallpaper.png')))
  self.image=image;self.cached=None;self.blur_cache=None;self.update()
 def resizeEvent(self,e):self.cached=None;self.blur_cache=None;super().resizeEvent(e)
 def wallpaper(self):
  if self.cached is None:
   scaled=self.image.scaled(self.size(),Qt.KeepAspectRatioByExpanding,Qt.SmoothTransformation);self.cached=scaled.copy(max(0,(scaled.width()-self.width())//2),max(0,(scaled.height()-self.height())//2),self.width(),self.height())
  return self.cached
 def blurred(self):
  if self.blur_cache is None:self.blur_cache=self.wallpaper().scaled(max(1,self.width()//22),max(1,self.height()//22),Qt.IgnoreAspectRatio,Qt.SmoothTransformation).scaled(self.size(),Qt.IgnoreAspectRatio,Qt.SmoothTransformation)
  return self.blur_cache
 def paintEvent(self,event):
  p=QPainter(self);p.drawPixmap(0,0,self.wallpaper());p.end()
class Shell:
 def __init__(self,preview=False):
  self.preview=preview;self.folder=Path.home();self.history=[];self.apps=applications();self.root=Backdrop();self.root.setWindowTitle('Laccaz Surface');self.root.setWindowFlags(Qt.FramelessWindowHint)
  geo=QApplication.primaryScreen().geometry();self.root.setGeometry(geo)
  self.panel=Dock(self.root);self.panel.setObjectName('dock');self.panel.setWindowTitle('Laccaz Dock');self.panel.setWindowFlags(Qt.Tool|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint);self.panel.setAttribute(Qt.WA_TranslucentBackground)
  rail=QHBoxLayout(self.panel);rail.setContentsMargins(13,10,13,10);rail.setSpacing(8)
  for index,(name,fn) in enumerate([('▦',lambda:self.show('apps')),('⌘',lambda:start('laccaz-devhub')),('▱',lambda:self.show('files')),('>_',lambda:start('konsole')),('▤',lambda:self.show('clips')),('◫',lambda:self.show('windows')),('A',lambda:start('laccaz-appcenter'))]):
   bt=DockButton(dock_icon(name,index),{'▦':'Приложения','⌘':'Dev Hub','▱':'Файлы','>_':'Терминал','▤':'Буфер обмена','◫':'Окна','A':'Центр приложений'}[name]);bt.clicked.connect(fn);rail.addWidget(bt)
  self.panel.adjustSize();self.panel.move(geo.x()+(geo.width()-self.panel.width())//2,geo.y()+geo.height()-self.panel.height()-14)
  self.bar=GlassPanel(self.root);self.bar.setWindowTitle('Laccaz Menu');self.bar.setWindowFlags(Qt.Tool|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint);self.bar.setGeometry(geo.x(),geo.y(),geo.width(),32);self.bar.setStyleSheet('QWidget{background:transparent;color:#20304b;font-size:12px;font-weight:600} QPushButton{border:0;background:transparent;padding:4px 10px;border-radius:6px} QPushButton:hover{background:rgba(255,255,255,55)}')
  menu=QHBoxLayout(self.bar);menu.setContentsMargins(18,0,18,0)
  for name,fn in [('Laccaz',self.home),('Проекты',lambda:self.show('projects')),('Приложения',lambda:self.show('apps')),('Окна',lambda:self.show('windows')),('Магазин',lambda:start('laccaz-appcenter'))]:
   bt=QPushButton(name);bt.clicked.connect(fn);menu.addWidget(bt)
  menu.addStretch();wall=QPushButton('Обои');wall.clicked.connect(self.choose_wallpaper);menu.addWidget(wall);control=QPushButton('Управление');control.clicked.connect(self.controls);menu.addWidget(control);self.clock=QLabel();menu.addWidget(self.clock);bt=QPushButton('Выход');bt.clicked.connect(self.logout);menu.addWidget(bt)
  self.drawer=QWidget();self.drawer.setWindowTitle('Laccaz Search');self.drawer.setWindowFlags(Qt.Tool|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint);self.drawer.resize(min(710,geo.width()-40),min(660,geo.height()-150));self.drawer.move(geo.x()+(geo.width()-self.drawer.width())//2,geo.y()+65)
  d=QVBoxLayout(self.drawer);d.setContentsMargins(24,18,24,24);d.setSpacing(14);d.addWidget(Titlebar(self.drawer,'Laccaz'));self.title=QLabel();self.title.setObjectName('brand');d.addWidget(self.title)
  self.search=QLineEdit();self.search.setPlaceholderText('Поиск…');self.search.textChanged.connect(self.populate);d.addWidget(self.search)
  self.list=QListWidget();self.list.itemActivated.connect(self.activate);self.list.itemClicked.connect(self.activate);d.addWidget(self.list)
  self.pause=QCheckBox('Пауза записи буфера');d.addWidget(self.pause)
  self.clearbutton=QPushButton('Очистить историю и системный буфер');self.clearbutton.clicked.connect(self.clear);d.addWidget(self.clearbutton)
  self.note=QLabel();self.note.setWordWrap(True);self.note.setObjectName('muted');d.addWidget(self.note)
  QApplication.clipboard().dataChanged.connect(self.clip_changed)
  self.timer=QTimer();self.timer.timeout.connect(self.tick);self.timer.start(1000);self.tick();self.root.show();self.panel.show();self.bar.show();self.create_widgets()
  if not preview:
   from surface_ipc import listen
   try:
    self.ipc,self.lock=listen();self.notifier=QSocketNotifier(self.ipc.fileno(),QSocketNotifier.Read);self.notifier.activated.connect(self.receive)
   except OSError as error:print('Surface shortcuts unavailable:',error,file=sys.stderr)
   QApplication.primaryScreen().geometryChanged.connect(self.relayout)
  if not preview:QTimer.singleShot(100,self.properties)
 def choose_wallpaper(self):
  path,_=QFileDialog.getOpenFileName(self.root,'Выбрать обои',str(Path.home()),'Изображения (*.png *.jpg *.jpeg *.webp)')
  if path:
   if QPixmap(path).isNull():QMessageBox.warning(self.root,'Обои','Не удалось прочитать изображение.');return
   self.root.settings.setValue('wallpaper',path);self.root.load_wallpaper(path);self.panel.update();self.bar.update()
   for w in self.widgets:w.update()
 def create_widgets(self):
  self.widgets=[]
  for x,width,height in [(28,185,160),(225,185,160),(28,382,108)]:
   panel=GlassPanel(self.root,self.root);panel.setGeometry(x,56 if height==160 else 228,width,height);layout=QVBoxLayout(panel);layout.setContentsMargins(18,14,18,14);self.widgets.append(panel)
  self.date_label=QLabel();self.date_label.setStyleSheet('font-size:14px;color:#d24442;font-weight:700');self.widgets[0].layout().addWidget(self.date_label);self.day_label=QLabel();self.day_label.setStyleSheet('font-size:46px;font-weight:300;color:#1c2b40');self.widgets[0].layout().addWidget(self.day_label);bt=QPushButton('Календарь');bt.clicked.connect(self.calendar);self.widgets[0].layout().addWidget(bt)
  self.time_label=QLabel();self.time_label.setStyleSheet('font-size:33px;font-weight:600;color:#1c2b40');self.widgets[1].layout().addWidget(self.time_label);self.widgets[1].layout().addWidget(QLabel('Местное время'));bt=QPushButton('Приложения');bt.clicked.connect(lambda:start('laccaz-appcenter'));self.widgets[1].layout().addWidget(bt)
  self.widgets[2].layout().addWidget(QLabel('ТВОЁ РАБОЧЕЕ ПРОСТРАНСТВО'));bt=QPushButton('Открыть Dev Hub →');bt.clicked.connect(lambda:start('laccaz-devhub'));self.widgets[2].layout().addWidget(bt)
  for widget in self.widgets:
   widget.setStyleSheet('QLabel{background:transparent;color:#29364e} QPushButton{background:rgba(255,255,255,95);border:0;border-radius:10px;padding:6px;color:#29364e;font-size:12px}')
   widget.show()
  self.tick()
 def calendar(self):
  if not hasattr(self,'calendar_window'):
   self.calendar_window=QWidget();self.calendar_window.setWindowTitle('Laccaz Calendar');self.calendar_window.setWindowFlags(Qt.Tool|Qt.FramelessWindowHint);v=QVBoxLayout(self.calendar_window);v.addWidget(Titlebar(self.calendar_window,'Календарь'));v.addWidget(QCalendarWidget());self.calendar_window.resize(480,400)
  self.calendar_window.show();self.calendar_window.raise_();self.calendar_window.activateWindow()
 def receive(self,*args):
  while True:
   try:action=self.ipc.recv(64).decode()
   except BlockingIOError:break
   if action=='desktop':start('wmctrl',['-k','on'])
   elif action in ('apps','clips','files','projects','windows'):self.show(action)
 def relayout(self,*args):
  geo=QApplication.primaryScreen().geometry();self.root.setGeometry(geo);self.bar.setGeometry(geo.x(),geo.y(),geo.width(),32);self.panel.move(geo.x()+(geo.width()-self.panel.width())//2,geo.y()+geo.height()-self.panel.height()-14);self.properties()
 def controls(self):
  if not hasattr(self,'control_panel'):
   self.control_panel=QWidget();self.control_panel.setWindowTitle('Laccaz Control Center');self.control_panel.setWindowFlags(Qt.Tool|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint);self.control_panel.resize(380,320);v=QVBoxLayout(self.control_panel);v.addWidget(Titlebar(self.control_panel,'Управление'))
   for name,cmd in [('Wi-Fi и подключения',['nm-connection-editor']),('Громкость и устройства',['pavucontrol']),('Dev Hub',['laccaz-devhub']),('Обзор окон',['laccaz-action','windows'])]:
    bt=QPushButton(name);bt.clicked.connect(lambda checked=False,c=cmd:start(c[0],c[1:]));v.addWidget(bt)
  geo=QApplication.primaryScreen().geometry();self.control_panel.move(geo.right()-400,geo.top()+48);self.control_panel.show();self.control_panel.raise_();self.control_panel.activateWindow()
 def properties(self):
  if not os.environ.get('DISPLAY'):return
  def prop(widget,key,kind,value):start('xprop',['-id',str(int(widget.winId())),'-f',key,kind,'-set',key,value])
  prop(self.root,'_NET_WM_WINDOW_TYPE','32a','_NET_WM_WINDOW_TYPE_DESKTOP');prop(self.panel,'_NET_WM_WINDOW_TYPE','32a','_NET_WM_WINDOW_TYPE_DOCK')
  prop(self.bar,'_NET_WM_WINDOW_TYPE','32a','_NET_WM_WINDOW_TYPE_DOCK')
  prop(self.panel,'_NET_WM_STRUT_PARTIAL','32c',f'0, 0, 0, 100, 0, 0, 0, 0, 0, 0, 0, {self.root.width()-1}')
  prop(self.bar,'_NET_WM_STRUT_PARTIAL','32c',f'0, 0, 32, 0, 0, 0, 0, 0, 0, {self.root.width()-1}, 0, 0');self.root.lower()
 def tick(self):
  now=QDateTime.currentDateTime();self.clock.setText(QLocale('ru_RU').toString(now,'ddd, d MMM   hh:mm'))
  if hasattr(self,'date_label'):self.date_label.setText(QLocale('ru_RU').toString(now,'dddd').upper());self.day_label.setText(now.toString('d'));self.time_label.setText(now.toString('hh:mm'))
 def home(self):self.drawer.hide();start('wmctrl',['-k','on'])
 def show(self,mode):
  self.mode=mode;self.search.clear();self.title.setText({'apps':'Приложения','clips':'Буфер обмена','projects':'Проекты','windows':'Окна','files':'Файлы'}[mode]);self.pause.setVisible(mode=='clips');self.clearbutton.setVisible(mode=='clips');self.populate();self.drawer.show();self.drawer.raise_();self.drawer.activateWindow();self.search.setFocus()
 def populate(self):
  if not hasattr(self,'mode'):return
  self.list.clear();q=self.search.text().casefold();rows=[]
  if self.mode=='apps':self.apps=applications();rows=[(n,p) for n,p in self.apps];self.note.setText('Поиск установленных приложений. Запуск по нажатию.')
  elif self.mode=='clips':rows=[(s,s) for s in self.history];self.note.setText('Только текст • до 40 записей в памяти • на диск не сохраняется. Выбери фрагмент, затем вставь Ctrl+V. Для паролей включай паузу.')
  elif self.mode=='files':
   self.note.setText(str(self.folder)+' • выбери папку или файл')
   try:rows=[('↑ На уровень выше',str(self.folder.parent))]+[(('▸ ' if p.is_dir() else '')+p.name,str(p)) for p in sorted(self.folder.iterdir(),key=lambda p:(not p.is_dir(),p.name.casefold())) if not p.name.startswith('.')]
   except OSError as e:self.note.setText(str(e));rows=[]
  elif self.mode=='projects':
   root=Path.home()/'Projects';root.mkdir(exist_ok=True);rows=[(p.name,str(p)) for p in sorted(root.iterdir()) if p.is_dir()];rows.insert(0,('+ Создать проект в Dev Hub','NEW'));self.note.setText('Проекты из ~/Projects. Выбор открывает папку.')
  else:
   self.note.setText('Выбери окно для переключения. Alt+Tab также работает.');self.windows();return
  for label,value in rows:
   if q in label.casefold():item=QListWidgetItem(label[:180]);item.setData(Qt.UserRole,value);self.list.addItem(item)
 def windows(self):
  p=QProcess(self.drawer);p.finished.connect(lambda code,status:self.window_result(p));p.start('wmctrl',['-l'])
 def window_result(self,p):
  if self.mode=='windows':
   for line in bytes(p.readAllStandardOutput()).decode(errors='replace').splitlines():
    parts=line.split(None,3)
    if len(parts)==4 and not parts[3].startswith('Laccaz ') and self.search.text().casefold() in parts[3].casefold():
     it=QListWidgetItem(parts[3]);it.setData(Qt.UserRole,parts[0]);self.list.addItem(it)
  p.deleteLater()
 def activate(self,item):
  value=item.data(Qt.UserRole)
  if self.mode=='apps':
   if not start('gio',['launch',value]):QMessageBox.warning(self.drawer,'Запуск','Не удалось запустить приложение.');return
  elif self.mode=='clips':QApplication.clipboard().setText(value)
  elif self.mode=='files':
   p=Path(value)
   if p.is_dir():self.folder=p;self.search.clear();self.populate();return
   QDesktopServices.openUrl(QUrl.fromLocalFile(value))
  elif self.mode=='projects':
   if value=='NEW':start('laccaz-devhub')
   else:QDesktopServices.openUrl(QUrl.fromLocalFile(value))
  else:start('wmctrl',['-ia',value])
  self.drawer.hide()
 def clip_changed(self):
  if self.pause.isChecked():return
  mime=QApplication.clipboard().mimeData()
  if not mime or mime.hasFormat('x-kde-passwordManagerHint') or not mime.hasText():return
  s=mime.text()
  if not s.strip() or len(s)>20000:return
  if s in self.history:self.history.remove(s)
  self.history.insert(0,s);del self.history[40:]
  if self.drawer.isVisible() and getattr(self,'mode','')=='clips':self.populate()
 def clear(self):self.history.clear();QApplication.clipboard().clear();self.populate()
 def logout(self):
  if QMessageBox.question(self.panel,'Завершить сеанс','Закрыть оболочку и выйти из сеанса?')==QMessageBox.Yes:QApplication.quit()
if __name__=='__main__':
 app=QApplication(sys.argv);app.setQuitOnLastWindowClosed(False);app.setStyle('Fusion');app.setStyleSheet(STYLE);shell=Shell('--preview' in sys.argv);sys.exit(app.exec())
