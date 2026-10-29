import os,socket,fcntl
from pathlib import Path

def directory():
 root=Path(os.environ.get('XDG_RUNTIME_DIR','/tmp'))/('laccaz-'+str(os.getuid()))
 root.mkdir(mode=0o700,exist_ok=True)
 if root.is_symlink() or root.stat().st_uid!=os.getuid():raise RuntimeError('Недопустимый каталог сеанса')
 root.chmod(0o700);return root

def listen():
 root=directory();lock=(root/'shell.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 path=root/'surface.sock';path.unlink(missing_ok=True);sock=socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM);sock.bind(str(path));path.chmod(0o600);sock.setblocking(False);return sock,lock

def send(action):
 if action not in ('apps','clips','files','projects','windows','desktop'):raise ValueError('Неизвестное действие')
 with socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM) as sock:sock.sendto(action.encode(),str(directory()/'surface.sock'))
