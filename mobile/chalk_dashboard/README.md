# Chalk Dashboard (Android)

Phone app for the shorts-studio dashboard. It reads the current tunnel address from a secret GitHub gist (written by `pipeline/linkgist.py`), signs in once with the setup code from the bot's `/app` command, and shows the dashboard. It accepts only `https://*.trycloudflare.com` addresses.

Build: `flutter build apk --release` (signing key in `secrets/android/`, never committed). Install: `adb install -r build/app/outputs/flutter-apk/app-release.apk`, or copy the APK to the phone.
