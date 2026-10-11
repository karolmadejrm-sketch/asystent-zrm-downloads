# Asystent ZRM — instalatory i aktualizacje

Publiczne repozytorium **wyłącznie do dystrybucji instalatorów**. Kod aplikacji, dane pacjentów, pliki keystore i hasła podpisujące **nie mogą być tutaj umieszczane**.

## Publikacja kolejnej wersji

1. Przejdź do [Releases](https://github.com/karolmadejrm-sketch/asystent-zrm-downloads/releases) → **Draft a new release**.
2. Utwórz tag wersji, np. `v1.5.30`. Jeśli wydanie jest testowe, zaznacz **Set as a pre-release**.
3. **Przed kliknięciem Publish release** dołącz instalatory w sekcji **Attach binaries / Assets**. Link do pliku w opisie wydania **nie** wystarcza.
4. Nazwij pliki zgodnie ze schematem:
   - Android: `Asystent-ZRM-Android-1.5.30-RELEASE.apk`
   - Windows: `Asystent_ZRM_Windows_1.5.30_AKTUALIZACJE.zip`
5. Publikuj wydanie. Workflow [Asystent ZRM - aktualizacje](../../actions/workflows/publish-update-manifests.yml) odczyta rzeczywiste Assets, wersje, SHA-256 i rozmiary; zaktualizuje JSON automatycznie.

## Kanały

- `updates/stable.json`: ostatnie **stabilne** instalatory (Releases bez zaznaczonego pre-release).
- `updates/beta.json`: ostatnie instalatory, także z wersji testowych.
- Jeśli publikujesz tylko Android albo tylko Windows, drugi instalator pozostanie z poprzedniego odpowiedniego wydania.
- Jeśli brak właściwego pliku w Assets albo sumy SHA-256, aktualizator **nie** reklamuje takiego pliku.
- Wersja Windows 1.5.29 sprawdza `/updates/stable.json` na Netlify, więc testowe wydania nie są automatycznie sugerowane posiadaczom stabilnej wersji.

## Przywracanie po niepełnej publikacji

Jeżeli pliki dodano **dopiero po opublikowaniu** wydania, przejdź do [Actions](../../actions/workflows/publish-update-manifests.yml) → **Run workflow**. Dodatkowo działa kontrola co 6 godzin. Nie trzeba ponownie publikować Netlify.

**Uwaga Android:** zawsze podpisuj kolejne APK tym samym oryginalnym kluczem produkcyjnym. Instalacja podpisana certyfikatem DEBUG nie zostanie nadpisana wersją produkcyjną i może wymagać ręcznej migracji danych.
