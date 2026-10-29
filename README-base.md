# Laccaz OS 0.1 — Developer Preview

Проект собственного дистрибутива Debian 13 amd64 с KDE Plasma и приложением Dev Hub.
**В архиве исходники и сборка, а не готовый ISO. ISO не собран; загрузка и установка не проверены.**

## Что входит
- KDE Plasma, Breeze Dark, собственная цветовая схема и обои: чёрный + лайм.
- Dev Hub на Python/PySide6: создание проектов Python/C/C++/JavaScript, открытие папок, Kate и Konsole, создание venv, Git init/status, Docker ps, запуск и остановка команд, вывод результата.
- GCC/G++, Clang, GDB, CMake, Ninja, Git, Python/venv/pip, Node.js/npm.
- Docker и Compose, SQLite, клиент PostgreSQL, ripgrep, htop, ShellCheck.
- Live-образ с Debian Installer в режиме live: установщик копирует настроенную систему.
- BIOS и UEFI предусмотрены конфигурацией; совместимость и Secure Boot ещё не проверены.

## Сборка на компьютере — рекомендуемый путь
Используй отдельную виртуальную машину Debian 13 (64-bit), 4 ядра, 8 ГБ ОЗУ и минимум 50 ГБ свободного места. Нужен интернет; загрузится несколько гигабайт. Не запускай сборку в своей основной системе Kali/Ubuntu или в WSL. Архив распакуй внутри Debian VM.

```bash
sudo apt update
sudo apt install live-build debootstrap debian-archive-keyring xorriso squashfs-tools dosfstools mtools syslinux-common isolinux grub-pc-bin grub-efi-amd64-bin ca-certificates
cd laccaz-os
sudo bash scripts/build.sh
```

Результат: `artifacts/laccaz-os-0.1-amd64.iso`, `SHA256SUMS` и логи. Проверка: `cd artifacts && sha256sum -c SHA256SUMS`.
Для повторной сборки сначала `sudo lb clean --purge` из каталога проекта. Не запускай несколько сборок одновременно. Это автоматизированный рецепт, не побитово воспроизводимая сборка: версии пакетов в репозиториях меняются.

## Сборка через GitHub
Создай собственный репозиторий, загрузи содержимое папки (включая `.github` и `auto`), открой Actions → Build Laccaz OS preview → Run workflow. После успешного выполнения скачай артефакт. Учти лимиты места/времени Actions: большой ISO может потребовать собственного runner. Workflow не был запущен в этой сессии.

## Проверка ISO перед реальным компьютером
1. Создай НОВУЮ виртуальную машину, 4–8 ГБ ОЗУ, пустой виртуальный диск 40 ГБ.
2. Подключи ISO как виртуальный DVD. Проверь загрузку Live, рабочий стол, сеть, раскладку и Dev Hub.
3. Создай и запусти все четыре шаблона. Команды ниже.
4. Перезагрузи VM и выбери графическую установку в меню ISO. Устанавливай только на пустой виртуальный диск. Установщик должен предложить создать пользователя и пароль; автоматической разметки в проекте нет.
5. Отключи ISO и проверь загрузку с диска, обычный вход, sudo, оформление, Dev Hub, сеть и обновления.
6. Повтори на BIOS и UEFI. До этого статус — непроверенный Developer Preview.

Live-пользователь — `developer`; это стандартная временная live-сессия Debian. Учётная запись установленной системы задаётся в установщике. Не используй Live как защищённую постоянную учётную запись.

## Запуск проектов
В Dev Hub создай проект; он появится в `~/Projects`. Терминал открывается в текущей папке.

Python: `python3 main.py`; окружение создаётся кнопкой Python venv, затем в терминале `source .venv/bin/activate`.
C: `make`, затем `./app`.
C++: `cmake -S . -B build`, затем `cmake --build build`, затем `./build/app`.
JavaScript: `npm start`.
Командное поле Dev Hub запускает одну программу с аргументами. Для `&&`, `|`, перенаправлений и интерактивных команд используй Konsole. Остановка действует на непосредственный процесс, не гарантирует завершение всех его потомков.
Docker: `sudo systemctl start docker`, затем `sudo docker run --rm hello-world` (нужен интернет). Пользователь намеренно не добавляется в группу docker. PostgreSQL server не установлен; имеется psql для подключения к внешнему серверу. Редактор по умолчанию — Kate; VS Code не включён.

## На флешку и реальный компьютер
Только после проверки VM: запиши ISO через Rufus (при запросе — DD mode) или balenaEtcher. Запись стирает флешку. Открой Boot Menu компьютера и выбери USB; ISO не «устанавливают в BIOS». Сначала Live, затем установка через загрузочное меню. Сделай резервную копию данных и сохрани ключ восстановления BitLocker, если есть Windows. При нескольких ОС используй ручную разметку и не форматируй разделы Windows/EFI. NVIDIA/Wi-Fi и сон требуют отдельной проверки на твоём оборудовании; проприетарный драйвер NVIDIA не настроен. Secure Boot может потребовать отдельной настройки.

## Структура и изменение
`auto/config` — параметры live-build; `config/package-lists` — пакеты;
`config/includes.chroot` — файлы будущей системы; `config/hooks` — сборочные настройки.
Dev Hub: `/usr/share/laccaz/devhub.py`; логика шаблонов: `core.py`.
Версии и ID Debian сохранены для совместимости; своё имя выводится через PRETTY_NAME и /etc/laccaz-release. Своего сервера обновлений нет: APT использует Debian. Обновление собственных компонентов пока через пересборку образа/ручную замену. Автоприменение обоев KDE — экспериментальное, зависит от инициализации Plasma.

## Источники
https://www.debian.org/releases/trixie/
https://manpages.debian.org/trixie/live-build/lb_config.1.en.html
https://live-team.pages.debian.net/live-manual/html/live-manual/customizing-installer.en.html
