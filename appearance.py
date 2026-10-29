from PySide6.QtCore import Qt,QRectF,QSize,QPropertyAnimation,QEasingCurve
from PySide6.QtGui import QColor,QPainter,QPen,QPixmap,QIcon,QLinearGradient
from PySide6.QtWidgets import QWidget,QHBoxLayout,QPushButton,QLabel,QAbstractButton
STYLE="""
QWidget{background:#f3f5f9;color:#202738;font-family:DejaVu Sans;font-size:13px}
QLabel{background:transparent} QLabel#brand{font-size:24px;font-weight:700;color:#29364e}
QLabel#hero{font-size:34px;font-weight:700} QLabel#muted{color:#758095}
QWidget#sidebar{background:#e5eaf3;border-radius:18px} QWidget#card{background:white;border:1px solid #e2e7f0;border-radius:18px}
QPushButton{background:#fff;border:1px solid #dfe4ed;border-radius:11px;padding:11px 15px;text-align:left}
QPushButton:hover{background:#e7edff;border-color:#b6c9fa} QPushButton:pressed{background:#d5e1ff}
QPushButton#primary{background:#3578ef;color:white;border:0;font-weight:600} QPushButton#primary:hover{background:#2569db}
QLineEdit,QComboBox{background:white;border:1px solid #dde3ec;border-radius:11px;padding:12px;selection-background-color:#b8d4ff}
QPlainTextEdit{background:#172032;color:#d6e3f7;border:0;border-radius:14px;padding:14px;font-family:monospace}
QListWidget{background:#fff;border:1px solid #e4e8f0;border-radius:15px;padding:9px}
QListWidget::item{padding:15px;border-bottom:1px solid #edf0f5}
QListWidget::item:selected{background:#e3edff;color:#2456a5;border-radius:8px}
QTabWidget::pane{background:#f5f7fb;border:1px solid #dce4f0;border-radius:14px} QTabBar::tab{background:#e5eaf3;padding:10px 20px;margin:3px;border-radius:8px} QTabBar::tab:selected{background:white;color:#2365cc} QGroupBox{background:white;border:1px solid #e2e7f0;border-radius:16px;margin-top:16px;padding:20px}
QGroupBox::title{subcontrol-origin:margin;left:20px;padding:0 6px}
QCheckBox{padding:9px} QScrollBar:vertical{width:9px;background:transparent} QScrollBar::handle:vertical{background:#bac4d4;border-radius:4px;min-height:25px}
"""
class WindowButton(QAbstractButton):
 def __init__(self,kind,parent=None):
  super().__init__(parent);self.kind=kind;self.setFixedSize(36,36);self.setCursor(Qt.PointingHandCursor)
  self.setToolTip({'close':'Закрыть','minimize':'Свернуть','maximize':'Развернуть / восстановить'}[kind]);self.setAccessibleName(self.toolTip());self.setObjectName('window_'+kind)
 def paintEvent(self,event):
  p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
  color={'close':'#ff6059','minimize':'#ffbd2e','maximize':'#28c840'}[self.kind]
  p.setBrush(QColor(color).darker(112) if self.isDown() else QColor(color));p.setPen(Qt.NoPen);p.drawEllipse(QRectF(6,6,24,24))
  p.setPen(QPen(QColor('#493b3c'),1.8))
  if self.kind=='close':p.drawLine(14,14,22,22);p.drawLine(14,22,22,14)
  elif self.kind=='minimize':p.drawLine(13,18,23,18)
  else:p.drawRect(14,14,8,8)
  p.end()
class Titlebar(QWidget):
 def __init__(self,window,title):
  super().__init__();self.target=window;row=QHBoxLayout(self);row.setContentsMargins(0,0,8,0);row.setSpacing(2);self.setMinimumHeight(44)
  self.buttons={}
  for kind,fn in [('close',self.close_target),('minimize',self.minimize),('maximize',self.zoom)]:
   button=WindowButton(kind);button.clicked.connect(lambda checked=False,action=fn:action());row.addWidget(button);self.buttons[kind]=button
  row.addSpacing(14);label=QLabel(title);label.setAttribute(Qt.WA_TransparentForMouseEvents);row.addWidget(label);row.addStretch()
 def close_target(self):self.target.close()
 def minimize(self):self.target.showMinimized()
 def zoom(self):self.target.showNormal() if self.target.isMaximized() else self.target.showMaximized()
 def mousePressEvent(self,event):
  if event.button()==Qt.LeftButton and self.target.windowHandle():self.target.windowHandle().startSystemMove()
 def mouseDoubleClickEvent(self,event):
  if event.button()==Qt.LeftButton:self.zoom()

def dock_icon(kind,index):
 pix=QPixmap(48,48);pix.fill(Qt.transparent);p=QPainter(pix);p.setRenderHint(QPainter.Antialiasing)
 colors=['#586bef','#8763dc','#4099e0','#34435c','#39aaa3','#ef9760','#468df5'];g=QLinearGradient(0,0,48,48);g.setColorAt(0,QColor(colors[index]));g.setColorAt(1,QColor(colors[index]).darker(125));p.setPen(Qt.NoPen);p.setBrush(g);p.drawRoundedRect(0,0,48,48,12,12);p.setPen(QPen(QColor('white'),2.3));p.setBrush(Qt.NoBrush)
 if index==0:
  for x in (13,24,35):
   for y in (13,24,35):p.drawEllipse(x-2,y-2,4,4)
 elif index==1:
  p.drawLine(18,14,10,24);p.drawLine(10,24,18,34);p.drawLine(30,14,38,24);p.drawLine(38,24,30,34);p.drawLine(27,11,21,37)
 elif index==2:
  p.drawRoundedRect(9,16,31,23,3,3);p.drawLine(10,16,10,11);p.drawLine(10,11,23,11);p.drawLine(23,11,28,16)
 elif index==3:
  p.drawLine(12,15,21,23);p.drawLine(21,23,12,31);p.drawLine(25,33,36,33)
 elif index==4:
  p.drawRoundedRect(12,11,25,29,3,3);p.drawRoundedRect(19,8,11,7,2,2);p.drawLine(18,24,31,24);p.drawLine(18,31,31,31)
 elif index==5:
  p.drawRoundedRect(8,10,25,22,3,3);p.drawRoundedRect(16,20,25,20,3,3)
 else:
  p.drawLine(12,34,24,11);p.drawLine(24,11,36,34);p.drawLine(10,28,38,28);p.drawLine(19,11,31,34)
 p.end();return QIcon(pix)

class DockButton(QPushButton):
 def __init__(self,icon,tip):
  super().__init__();self.setIcon(icon);self.setIconSize(QSize(46,46));self.setFixedSize(62,62);self.setToolTip(tip);self.setCursor(Qt.PointingHandCursor)
  self.setStyleSheet('QPushButton{background:transparent;border:0;padding:0} QPushButton:hover{background:rgba(255,255,255,130);border-radius:18px}')
  self.anim=QPropertyAnimation(self,b'iconSize');self.anim.setDuration(140);self.anim.setEasingCurve(QEasingCurve.OutCubic)
 def scale(self,size):self.anim.stop();self.anim.setStartValue(self.iconSize());self.anim.setEndValue(QSize(size,size));self.anim.start()
 def enterEvent(self,e):self.scale(57);super().enterEvent(e)
 def leaveEvent(self,e):self.scale(46);super().leaveEvent(e)
