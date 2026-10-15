# Gym Log (Android)
FastAPI + SQLite работают прямо внутри приложения (Chaquopy), интерфейс — WebView.
Сервер стартует сам при открытии приложения, база лежит в памяти приложения.

## Как получить .apk
**Вариант 1 (без Android Studio):** залейте папку в новый репозиторий на GitHub →
вкладка Actions → Build APK → после сборки скачайте артефакт `gym-log-apk` (app-debug.apk).

**Вариант 2:** откройте папку в Android Studio → Build → Build APK(s).
