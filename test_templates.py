import importlib.util, pathlib, subprocess, tempfile, unittest, shutil
root=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('core',root/'config/includes.chroot/usr/share/laccaz/core.py');core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
class Templates(unittest.TestCase):
 def test_templates(self):
  with tempfile.TemporaryDirectory() as d:
   for lang in core.TEMPLATES:
    p=core.create_project(d,lang.replace("+","p"),lang)
    if lang=='Python':cmd=['python3','main.py']
    elif lang=='JavaScript':cmd=['node','main.js']
    elif lang=='C':
     subprocess.run(['make'],cwd=p,check=True,capture_output=True);cmd=['./app']
    else:
     subprocess.run(['cmake','-S','.','-B','build'],cwd=p,check=True,capture_output=True)
     subprocess.run(['cmake','--build','build'],cwd=p,check=True,capture_output=True);cmd=['./build/app']
    r=subprocess.run(cmd,cwd=p,capture_output=True,text=True,check=True)
    self.assertEqual(r.stdout.strip(),'Hello from Laccaz OS!')
 def test_no_escape_or_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   for name in ['../escape','a/b','', 'x;id']:
    with self.assertRaises(ValueError):core.create_project(d,name,'Python')
   p=core.create_project(d,'demo','Python');(p/'main.py').write_text('keep')
   with self.assertRaises(FileExistsError):core.create_project(d,'demo','Python')
   self.assertEqual((p/'main.py').read_text(),'keep')
if __name__=='__main__':unittest.main()
