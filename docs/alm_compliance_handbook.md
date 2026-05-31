# Ludus Magnus ALM - Uyumluluk ve Gereksinim El Kitabı
## Belge Kodu: LM_ALM_HB_001
## Sistem Durumu: YAYINLANDI (ASPICE LEVEL 3 UYUMLU)

Bu el kitabı, Ludus Magnus ALM (Application Lifecycle Management) platformunun gereksinim yazma kurallarını, proje geliştirme standartlarını, git entegrasyon politikalarını ve kullanıcı talepleri doğrultusunda sisteme kazandırılan tüm geliştirmeleri barındıran resmi başvuru kılavuzudur.

---

## 1. UYUMLULUK BAĞLAMI VE ROL SORUMLULUKLARI

ASPICE ve V-Model mühendislik çerçeveleri altında, tüm tasarım dökümanları **Sistem Gereksinimleri**, tüm kodlama commitleri ve test raporları ise dinamik **Sistem Doğrulama Kayıtları** olarak kabul edilir. Geliştirme süreci, dökümantasyon sınırları netleştirilmiş 4 ana mühendislik rolüne bölünmüştür:

*   **Game Director / Product Owner (`@prime`):**
    *   *Sorumluluk Alanı:* Seviye 0 (Vision Document / VD) ve Seviye 1 (Game Design Document / GDD, Narrative Design Document / NDD).
    *   *Görevi:* Pantheon sınırlarını, oyun mekaniklerini ve temel oynanış matematiğini belirler. Tasarım bütünlüğünü korur.
*   **Technical Director / Lead Architect (`@arch`):**
    *   *Sorumluluk Alanı:* Seviye 3-C (Technical Design Document / TDD).
    *   *Görevi:* Bellek tahsislerini, Blueprint kalıtım kurallarını, C++ sınıflarını ve performans bütçelerini yönetir.
*   **Art & Audio Director (`@virtuoso`):**
    *   *Sorumluluk Alanı:* Seviye 3-D (Art & Audio Design Document / ADD).
    *   *Görevi:* Sprite billboard işleme bütçelerini, ses örnekleme hızlarını, Niagara VFX sınırlarını ve doku çözünürlüklerini planlar.
*   **Producer / QA Lead (`@pub`):**
    *   *Sorumluluk Alanı:* Seviye 4 (Product Backlog Item / PBI) ve Seviye 5 (Quality Assurance / Test Case - TC_QA).
    *   *Görevi:* Kabul Kriterlerini (AC), Bitiş Tanımını (DoD), sprint planlamasını ve test doğrulama süreçlerini yönetir.

---

## 2. 6 SEVİYELİ GEREKSİNİM HİYERARŞİSİ VE YAZIM STANDARTLARI

Her tasarım kararı, en üst seviye vizyondan en alt seviye kod satırına ve doğrulama testine kadar izlenebilir olmak zorundadır. Seviyeler ve isimlendirme kuralları aşağıdaki gibidir:

```text
L0: Vizyon Belgesi (VD.md)  ──>  [REQ_VD_XXX_00]
     │
     └──> L1: Oyun Tasarım Belgesi (GDD.md) ──> [REQ_GDD_XXX_00]
           │
           ├──> L2: Anlatı Tasarım Belgesi (NDD.md) ──> [REQ_NDD_XXX_00]
           │
           ├──> L3-C: Teknik Tasarım Belgesi (TDD.md) ──> [REQ_TDD_XXX_00]
           │
           └──> L3-D: Sanat & Ses Tasarım Belgesi (ADD.md) ──> [REQ_ADD_XXX_00]
                 │
                 └──> L4: Product Backlog Kalemi (PBI.md) ──> [PBI_XXX]
                       │
                       └──> L5: QA Test Senaryosu (QA.md) ──> [TC_QA_XXX_PBIYYY_Z]
```

### Seviye Kuralları ve Token Formatları

1.  **Level 0: Vision Document (`VD.md`)**
    *   *Token Formatı:* `[REQ_VD_XXX_00]` (Örn: `XXX` = `SCP` Kapsam, `TEC` Teknik Kısıt, `ART` Sanat).
    *   *Zorunlu İçerik:* Hedef platform (Steam/PC), kare hızı (FPS) standartları, hedef donanım bütçeleri ve temel oyun döngüsü.
2.  **Level 1: Game Design Document (`GDD.md`)**
    *   *Token Formatı:* `[REQ_GDD_XXX_00]` (Örn: `XXX` = `SYS` Genel Sistemler, `CMB` Dövüş, `ECO` Ekonomi, `STY` Stil).
    *   *Zorunlu İçerik:* Matematiksel döngü formülleri, oyuncu girdileri ve sistem konfigürasyonları.
3.  **Level 2: Narrative Design Document (`NDD.md`)**
    *   *Token Formatı:* `[REQ_NDD_XXX_00]` (Örn: `XXX` = `LOR` Lore, `QST` Görevler, `DLG` Diyaloglar).
    *   *Zorunlu İçerik:* Görev düğümleri, karakter diyalog şemaları ve dünya kuralları.
4.  **Level 3-C: Technical Design Document (`TDD.md`)**
    *   *Token Formatı:* `[REQ_TDD_XXX_00]` (Örn: `XXX` = `SYS` Teknik Altyapı, `CMB` Fizik ve Dövüş Kod Yapısı).
    *   *Zorunlu İçerik:* Blueprint/C++ sınıf sınırları, bellek bütçeleri ve veri tabloları.
5.  **Level 3-D: Art & Audio Design Document (`ADD.md`)**
    *   *Token Formatı:* `[REQ_ADD_XXX_00]` (Örn: `XXX` = `STY` Stil, `TEX` Doku, `ANM` Animasyon, `AUD` Ses).
    *   *Zorunlu İçerik:* Doku boyutu tahsisleri, ses kanalı sınırları ve parça/partikül limitleri.
6.  **Level 4: Product Backlog Item (`PBI.md` or files under `/PBI/`)**
    *   *Token Formatı:* `[PBI_XXX]` (Örn: `XXX` = 3 haneli sayı dizisi `[PBI_042]`).
    *   *Zorunlu İçerik:* Story point puanları, Kabul Kriterleri (AC) ve Bitiş Tanımı (DoD) işaretleri.
7.  **Level 5: Quality Assurance (`QA.md` or files under `/QA/`)**
    *   *Token Formatı:* `[TC_QA_XXX_PBIYYY_Z]` (Örn: `XXX` = Modül, `YYY` = İlişkili PBI numarası, `Z` = Test sırası: `[TC_QA_CMB_PBI042_A]`).
    *   *Zorunlu İçerik:* Ön koşullar, adımlar, beklenen çıktılar ve durum etiketleri (`PASS`, `FAIL`, `BLOCKED`).

---

## 3. İLİŞKİSEL BAĞLANTI VE İZLENEBİLİRLİK (TRACEABILITY)

Sağlam bir ALM yapısı için gereksinimler arasında çift yönlü izlenebilirlik (upstream ve downstream) zorunludur. İlişkisel bağlar döküman açıklamalarının içerisine doğrudan hedef token yerleştirilerek kurulur:

*   **Yukarı Doğru İzlenebilirlik (Upstream):** Alt seviye bir gereksinim, bağlı olduğu üst seviye gereksinimin tokenını referans göstermelidir.
    *   *Örnek GDD Tanımı (L1 -> L0):* 
        `[REQ_GDD_CMB_01] Karakter dövüş sistemi mekanik yorgunluğu önlemek için 3 farklı kombo içerir. Referans: [REQ_VD_SCP_02].`
*   **Aşağı Doğru İzlenebilirlik (Downstream):** PBIs ve Test Senaryoları, doğruladıkları teknik spesifikasyonları ve anlatı tasarımlarını belirtmelidir.
    *   *Örnek QA Testi Tanımı (L5 -> L3-C ve L4):* 
        `[TC_QA_CMB_PBI042_A] Çift Zıplama Fiziği Doğrulaması. Hedef: [REQ_TDD_CMB_12], Doğrulanan İş Kalemi: [PBI_042].`

---

## 4. GIT BRANCHING VE SÜRÜM-COMMIT STANDARTLARI

Kod değişikliklerinin doğrudan sistem gereksinimleriyle eşleştirilebilmesi için aşağıdaki Git standartları uygulanır:

### Dal (Branch) İsimlendirme Kuralları
- **Ana Geliştirme Dalı:** `develop` veya `main`.
- **Özellik Dalları:** `feature/PBI_XXX-kisa-aciklama` (Örn: `feature/PBI_042-double-jump`).

### Commit Mesaj Formatı
Özellik dallarındaki her commit, versiyon-commit aşama notasyonuyla başlamalıdır:
- `vA.B` sprint seviyesindeki ana sürümü belirtir (Örn: Sprint 1 için `v0.1`).
- `vA.B:C` özellik seviyesindeki commit sırasını belirtir (`C` = commit sırası).

Mesaj içeriğinde hedeflenen PBI tokenı ve ilişkili teknik gereksinim tokenı mutlaka yer almalıdır:
- *Format:* `vA.B:C - [PBI_XXX] - [Açıklama] [REQ_TOKEN]`
- *Örnek:* `v0.1:04 - [PBI_042] - Karakter cift ziplama fizik degerleri eklendi [REQ_TDD_CMB_12]`

---

## 5. STATİK DENETİM VE UYUMLULUK ANALİZ KURALLARI

Sistem denetiminden (Audit) geçebilmek için dökümanlar sıfır mimari hata ile korunmalıdır. Python compliance engine bu denetimleri şu kurallarla yapar:
1.  **Orphan Rule (Yetim Gereksinim):** L1-L3 seviyesindeki (GDD, NDD, TDD, ADD) her gereksinimin en az bir L0 Vision (VD) parent tokenına yukarı doğru bağı olmalıdır. Bu bağı olmayan gereksinimler **Orphan Error (Yetim Hatası)** olarak raporlanır.
2.  **QA Coverage Rule (Test Açığı):** Her L4 Product Backlog Item (PBI) kalemi, en az bir adet L5 `TC_QA` doğrulama senaryosuna bağlı olmalıdır. Test senaryosu olmayan PBIs kalemleri **QA Test Gap (Test Açığı)** olarak raporlanır.
3.  **Stability Rule (Stabilite):** Herhangi bir test senaryosu `FAIL` veya `BLOCKED` durumundaysa, ilişkili PBI ve tüm aşağı akış bileşenleri kilitlenir. Sürüm yayınlama durumu kararsız olarak raporlanır.

---

## 6. KULLANICI TALEPLERİ VE UYGULANAN GELİŞTİRMELER

Kullanıcının ALM platformunun geliştirilmesi sürecindeki tüm tariflemeleri, kararları ve talepleri aşağıda kronolojik ve madde madde açıklanmıştır:

### talep 1: Çoklu Proje (Multi-Project) ve Dinamik Port Yönetimi
- **Kullanıcı Tarifi:** ALM her proje için ayrı ayrı "proje" sayfaları oluştursun. Her projenin yerel dizin linkini ve GitHub linklerini alsın. Tekrar tekrar geliştirme yapmak gerekmesin.
- **Gerçekleştirilen Geliştirme:** Sistem `projects.json` tabanlı çoklu proje kayıt sistemine geçirildi. Arayüze dinamik `+ Add Project` modalı eklendi. Sunucu port çakışmalarını veya yetki engellerini aşmak için dinamik port tarama (port 8000 meşgulse otomatik 8001, 8002...) mekanizması entegre edildi.

### talep 2: Anlık Güncelleme ve Refresh Butonu
- **Kullanıcı Tarifi:** Dokümanlar güncellenmişse veya repoda bir güncelleme varsa ALM içerisinde bu güncellemeyi görebilmek için bir refresh/update butonu olsun. Arka planda bu güncellemeyi sağlayacak komutu çalıştırsın.
- **Gerçekleştirilen Geliştirme:** Arayüzün sağ üst köşesine **"Refresh System"** butonu yerleştirildi. Bu buton sunucuya asenkron bir POST isteği gönderir. Sunucu arka planda anlık olarak markdown taraması ve git analizini sıfırdan yaparak JSON veritabanını yeniler ve arayüzü kesintisiz olarak günceller.

### talep 3: Arayüz Düzeni ve Görselleştirmelerin Ayrılması (Multi-Page Yapısı)
- **Kullanıcı Tarifi:** Obsidian (vis.js) arayüzü çok yer kaplıyor ve akıcı değil. Ayrı bir sayfada bulunsun. Gereksinimleri tablo ya da Jira benzeri bir arayüzde görebileceğim sayfa ana sayfa olsun. Piramit ağaç ve obsidian farklı sayfalarda olsun, tek sayfaya sığdırma.
- **Gerçekleştirilen Geliştirme:** Arayüz **sekme bazlı multi-page (çok sayfalı)** yapıya kavuşturuldu:
  - **Document Navigator (Ana Sayfa):** Sol tarafta nested tree gezgini, sağ/orta tarafta geniş spesifikasyon detay paneli.
  - **Kanban Board:** Jira benzeri kartlı yaşam döngüsü panosu.
  - **Grid View:** Arama ve filtreleme yapılabilen matris tablosu.
  - **Obsidian Graph:** Ayrı sekmeye taşınmış ilişkisel ağ grafiği.
  - **Focus Pyramid Tree:** Ayrı sekmeye taşınmış hiyerarşik piramit görünümü.

### talep 4: Genişletilmiş Detay Paneli (Drawer)
- **Kullanıcı Tarifi:** Board view'da tıklanan gereksinim detayları sağda çok küçük gözüküyor, o kısmın büyük olmasını istiyorum.
- **Gerçekleştirilen Geliştirme:** Kanban Board, Grid View ve Obsidian sayfalarındaki kartlara tıklandığında sağdan açılan detay çekmecesinin (`detail-drawer`) genişliği ekranın **%60 (veya minimum 800px)** alanını kaplayacak şekilde genişletildi. Yazı boyutları ve padding oranları bu genişliğe göre ferahlatılarak specifications alanı son derece okunaklı hale getirildi.

### talep 5: Kanban Board - L3 Sütunlarının Ayrılması
- **Kullanıcı Tarifi:** Board view'da L3'ler de kendi arasında ayrılsın (TDD, ADD vb. diye). Tek bir çatıda değerlendirme onları.
- **Gerçekleştirilen Geliştirme:** Kanban tablosundaki "L3 Specs" sütunu tamamen kaldırılarak yerine **L3-C Technical (TDD)** ve **L3-D Art & Audio (ADD)** adlarında iki ayrı, bağımsız sütun oluşturuldu. Gereksinimler otomatik olarak ilgili alt disiplin sütunlarında listelenmektedir.

### talep 6: Kanban Board - Sütun Daraltma (Toggle) Mekanizması
- **Kullanıcı Tarifi:** Board view'de de toggle (daraltma) yapısı olsun.
- **Gerçekleştirilen Geliştirme:** Her bir Kanban sütununun başlığına tıklandığında sütunun dikey olarak daraltılmasını (toggle) sağlayan JS/CSS mekanizması eklendi. Sütun daraltıldığında kartlar gizlenir, sütun ince dikey bir şeride dönüşür ve sütun başlığı dikey olarak (vertical text-orientation) şık bir biçimde yazılır.

### talep 7: Ego-Centric Focus Tree (Performans ve Sadeleştirme)
- **Kullanıcı Tarifi:** Piramid tree yapısı çok verimsiz. Sadece seçilen gereksinim için gösterecek şekilde güncelle o kısmı. Boş gözüksün, L0 seçildiği zaman L0 gözüksün.
- **Gerçekleştirilen Geliştirme:** Focus Pyramid Tree sekmesi açıldığında seçili düğüm yoksa ekranda "Focus Tree Görünümü Boş - Lütfen bir gereksinim seçin" uyarısı gösterilir. Sol ağaçtan veya panodan bir gereksinim seçildiğinde, ağaç sadece o düğümü, onun doğrudan ebeveynlerini ve çocuklarını hiyerarşik olarak (3 katmanlı) çizer. Seçilen düğüm kalın çerçeve ve mavi parlama (glow) efektiyle merkez olarak vurgulanır.

### talep 8: Git Log Performans Optimizasyonu (Kilitlenme Çözümü)
- **Kullanıcı Tarifi:** Yenileme butonu bazen kilitleniyor veya "Refresh failed" hatası veriyor, bu problemi çöz.
- **Gerçekleştirilen Geliştirme:** Python compliance motorundaki `git log` tarama komutuna son 150 commit sınırı (`-n 150`) eklendi. Bu sayede tarama ve analiz süresi **94 saniyeden sadece 3 saniyeye indirilerek** kilitlenme ve timeout kaynaklı "Refresh failed" hatası tamamen ortadan kaldırıldı.
