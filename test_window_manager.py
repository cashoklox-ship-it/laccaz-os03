"""Run under X11 with Openbox and the shipped config/theme; real OS mouse clicks."""
import subprocess,time,re
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QLabel
from PySide6.QtTest import QTest
app=QApplication([]);app.setQuitOnLastWindowClosed(False);w=QWidget();w.setWindowTitle('Native Decoration Probe');w.resize(600,350);w.move(280,180);v=QVBoxLayout(w);v.addWidget(QLabel('Native Openbox controls'));w.show();QTest.qWait(300)
def click(index):
 f=w.frameGeometry();g=w.geometry();top=g.y()-f.y()
 # Openbox theme: 8px padding, one-pixel border, button ~= font height.
 button=top-18;y=f.y()+top//2;x=f.x()+11+button//2+index*(button+10)
 subprocess.run(['xdotool','mousemove',str(x),str(y),'click','1'],check=True);QTest.qWait(200)
print('Native frame height:',w.geometry().y()-w.frameGeometry().y(),flush=True)
click(1);assert w.isMinimized(),'native minimize did not work'
w.showNormal();w.raise_();w.activateWindow();QTest.qWait(200)
click(2);assert w.isMaximized(),'native maximize did not work'
click(2);assert not w.isMaximized(),'native restore did not work'
click(0);assert not w.isVisible(),'native close did not work'
print('PASS native Openbox close/minimize/maximize mouse clicks')
