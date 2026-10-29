"""No package changes. UI transactions use a fake pkexec executable."""
import importlib.machinery,importlib.util,json,os,sys,tempfile,time
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from PySide6.QtWidgets import QApplication,QMessageBox
from PySide6.QtTest import QTest
r=Path(__file__).resolve().parents[1];src=r/'config/includes.chroot/usr/share/laccaz';sys.path.insert(0,str(src))
from appcenter import AppCenter
from appearance import STYLE
helper_path=r/'config/includes.chroot/usr/libexec/laccaz-package-action';loader=importlib.machinery.SourceFileLoader('package_helper',str(helper_path));spec=importlib.util.spec_from_loader(loader.name,loader);helper=importlib.util.module_from_spec(spec);loader.exec_module(helper)
allowed={a['package'] for a in json.loads((src/'catalog.json').read_text())}
assert helper.command('install','vlc',allowed)==['/usr/bin/apt-get','--yes','--no-remove','install','vlc']
for args in [('install','-oAPT::Update::Pre-Invoke=bad'),('install','vlc;id'),('remove','bash'),('update','vlc')]:
 try:helper.command(*args,allowed)
 except ValueError:pass
 else:raise AssertionError(args)
with patch.object(helper,'CATALOG',src/'catalog.json'),patch.object(helper.os,'geteuid',return_value=0),patch.object(helper.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='Remv vlc [1]\nRemv important-package [1]\n')) as run:
 # The authoring catalogue is owned by root. No actual root command executes.
 try:helper.main(['remove','vlc'])
 except ValueError as e:assert 'important-package' in str(e)
 else:raise AssertionError('Unsafe removal allowed')
 assert run.call_count==1
print('PASS catalogue allowlist, argv validation and collateral removal refusal')
app=QApplication([]);app.setStyle('Fusion');app.setStyleSheet(STYLE);w=AppCenter();w.show()
def wait(fn):
 deadline=time.monotonic()+5
 while not fn() and time.monotonic()<deadline:app.processEvents();QTest.qWait(15)
 assert fn(),'UI timeout'
wait(lambda:w.check is None)
assert len(w.catalog)==20
w.search.setText('vlc');assert w.list.count()==1
w.filter_category('Творчество');assert w.list.count()==0
w.search.clear();assert w.list.count()==4
w.filter_category('Все');w.search.setText('vlc');assert w.selected()['package']=='vlc'
with tempfile.TemporaryDirectory() as d:
 exe=Path(d)/'pkexec';exe.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\nexit 126\n');exe.chmod(0o755)
 old=os.environ['PATH'];os.environ['PATH']=d+':'+old
 try:
  with patch.object(QMessageBox,'question',return_value=QMessageBox.Yes):w.transaction('install','vlc')
  wait(lambda:w.proc is None and w.check is None)
  assert 'отменено' in w.status.text(),w.status.text()
  assert '--disable-internal-agent' in w.log.toPlainText()
  exe.write_text('#!/bin/sh\nprintf "FAKE_TRANSACTION_OK\\n"\nexit 0\n');exe.chmod(0o755)
  with patch.object(QMessageBox,'question',return_value=QMessageBox.Yes):w.transaction('refresh')
  wait(lambda:w.proc is None and w.check is None)
  assert w.status.text()=='Операция завершена.'
 finally:os.environ['PATH']=old
w.grab().save(str(r/'previews/app-center.png'));w.close()
print('PASS App Center filters, dpkg status query, simulated authorization cancellation/success')
