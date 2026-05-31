# 🛡️ Ludus Magnus Custom ALM — ASPICE Level 3 Traceability Engine & Portal

Ludus Magnus Custom ALM, ASPICE Level 3 uyumluluk denetimleri ve dikey/yatay gereksinim izlenebilirliği (traceability) sunan, tam offline destekli (offline-first) ve lokal web arayüzüne sahip yeni nesil bir Application Lifecycle Management (ALM) sistemidir.

Bu yazılım, oyun stüdyolarının ve büyük mühendislik ekiplerinin gereksinim dökümanlarını (VD, GDD, NDD, TDD, ADD, PBI, QA) otomatik olarak tarar, aralarındaki ilişkisel bağları çıkarır ve 12 ASPICE denetim kuralına göre statik analizler gerçekleştirir.

---

## ✨ Öne Çıkan Özellikler

### 1. ⚙️ Çoklu Proje Destekli Python Parser Motoru
- **Markdown AST Parser:** `.md` dökümanlarındaki gereksinimleri 3 farklı kalıpta (Tablo Satırı, Başlık, Liste) otomatik olarak ayrıştırır.
- **İlişkisel Bağlayıcı:** Çoklu token eşleşmesi, bağlam izleme, referans kalıpları ve ön koşul bloklarını analiz eden 4 aşamalı yönlü çizge (graph) oluşturucu.
- **Manuel Gereksinim Ekleme (Override):** Otomatik taramanın yetersiz kaldığı durumlarda `manual_requirements.json` ve `manual_edges.json` üzerinden manuel veri birleştirme (merge) desteği.

### 2. 🛡️ 12 Aşamalı ASPICE Level 3 Denetim Motoru
- **Orphan (Yetim) Düğüm Kontrolü:** Tüm alt katman gereksinimlerinin en az bir L0 (Vizyon) hedefine dikey olarak ulaştığını BFS/DFS ile doğrular.
- **QA & Test Kapsamı:** PBIs-QA eşleşmelerini denetler. Başarısız (**FAIL**) test senaryolarına bağlı PBIs'ları otomatik olarak kilitler (`STABILITY_BLOCK`).
- **Uyum Sağlık Skoru:** Toplam ihlal/gereksinim oranına göre gerçek zamanlı sağlık yüzdesi (%0 - %100) hesaplar.
- **Fibonacci & DoD Kontrolleri:** PBI'ların Story Point Fibonacci serisine uyumunu ve Definition of Done kontrol listelerini denetler.

### 3. 📸 Gelişmiş Codebeamer Özellikleri
- **Dalga Etki Analizi (Impact Analysis):** Seçili bir gereksinim değiştiğinde etkilenen tüm alt katman downstream düğümleri recursive olarak çıkarır ve %risk skoru hesaplar.
- **Baseline Yönetimi & Fark Analizi (Diff):** Proje durumunun anlık dondurulmuş (baseline) snapshot'ını alır. İki dondurulmuş sürüm arasındaki eklenen, silinen ve değişen gereksinim mutasyonlarını listeler.
- **Git Entegrasyonu:** Commit loglarını tarayarak dikey entegrasyonu ve aktif branch listelerini arayüze taşır.

### 4. 🌐 Premium Dark Glassmorphic Arayüz (SPA)
Tamamen offline-first mimaride, **Cytoscape.js** yerel kütüphanesiyle CDN bağımlılığı olmadan çalışan **7 sekmeli monolitik SPA portalı**:
1. **Doküman Gezgini:** Klasör bazlı accordion ağaç gezintisi ve %60 genişlikte sağ detay paneli.
2. **Kanban Tahtası:** 7 seviyeli (L0 - L5) WIP limitli ve daraltılabilir Kanban sütunları.
3. **Tablo Görünümü:** Filtrelenebilir, sıralanabilir gereksinim tablosu ve CSV/JSON export aracı.
4. **Obsidyen Ağ Grafiği:** Fizik simülasyonlu, trace depth derinlik kısıtlamalı ve interaktif **Ripple Effect** animasyonlu etki çizgesi.
5. **Focus Piramidi:** L0 hedeflerinden aşağı doğru accordion mantığıyla genişleyen okunaklı pyramid görselleri.
6. **Kapsam Matrisi:** L0 satırları × L1-L5 sütunları arasındaki izlenebilirlik durumu (Bağlı/Eksik) ve **Eksik Gereksinimler Listesi**.
7. **Sprint Dashboard:** Sağlık skoru, QA durumları, baseline karşılaştırma aracı ve Git commit zaman çizgisi.

---

## 📂 Dizin Yapısı

```
C:\repo\7_CustomALM\
├── alm_orchestrator.py              # Giriş (CLI + HTTP Server, port 8002)
├── projects.json                    # Çoklu proje kayıt deposu
├── run_alm.bat                      # Çift tıklanabilir Windows launcher
├── _LM_ALM_System/
│   ├── alm_portal.html              # Premium web portalı (SPA)
│   ├── lib/
│   │   └── cytoscape.min.js         # Yerel offline grafik kütüphanesi
│   └── alm_offline_data/
│       └── {project_id}.json        # Çevrimdışı JSON snapshot veri tabanı
├── engine/
│   ├── __init__.py
│   ├── ast_parser.py                # Markdown AST tarayıcı
│   ├── traceability_builder.py      # Çizge ilişkileri kurucu
│   ├── git_analyzer.py              # Git log & branch analizörü
│   ├── audit_engine.py              # 12 ASPICE denetim kuralı
│   ├── impact_analyzer.py           # Downstream etki analizi
│   ├── baseline_manager.py          # Baseline snapshot ve karşılaştırma
│   └── project_manager.py           # projects.json CRUD ve scan orkestrasyonu
├── docs/
│   ├── PATTERN_RULES.md             # Gereksinim & Git kuralları el kitabı
│   ├── CONFIGURATION_GUIDE.md       # Konfigürasyon ve port rehberi
│   ├── USER_TODO.md                 # Kullanıcı operasyon test rehberi
│   └── alm_compliance_handbook.md   # ALM vizyon dokümanı
└── rules/
    └── 0_GeneralDocumentationRules.md # ASPICE standart kuralları
```

---

## 🚀 Kurulum ve Oynanış Yönergesi

### Gereksinimler:
- Python 3.x (Sadece standart kütüphaneler kullanılır, ek paket yüklemeye gerek yoktur).
- Git (Commit loglarını ve branch'leri okumak için).

### Çalıştırma:
1. Proje dizinindeki **`run_alm.bat`** dosyasına çift tıklayın.
2. Bu dosya sunucuyu arka planda başlatacak ve tarayıcınızda [http://localhost:8002/](http://localhost:8002/) portalını otomatik açacaktır.
3. Sağ üst köşedeki **"🔄 Refresh System"** butonuna basarak ilk tam kapsamlı dikey taramayı tetikleyebilirsiniz.

---

## 🛠️ CLI Kullanım Kılavuzu

Sunucu modundan bağımsız olarak CLI parametreleri ile hızlı tarama ve sürüm dondurma işlemlerini koşturabilirsiniz:

- **Web Portalı Başlatma:** `python alm_orchestrator.py --serve`
- **Port Belirtme:** `python alm_orchestrator.py --serve --port 8080`
- **Sadece Scan Etme & Çevrimdışı JSON İhracı:** `python alm_orchestrator.py --scan`
- **Baseline Snapshot Alıp Dondurma:** `python alm_orchestrator.py --baseline "Sprint_2_Final"`
