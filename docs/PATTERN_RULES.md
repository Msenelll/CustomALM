# Ludus Magnus ALM — ASPICE Level 3 Belgelendirme Standartları ve Kalıpları (PATTERN_RULES.md)

Bu doküman, Ludus Magnus ALM sisteminin markdown dosyalarından gereksinimleri (requirements), iş paketlerini (PBI) ve test senaryolarını (QA Test Cases) çıkarırken tanıdığı resmi kalıpları, token biçimlerini ve ilişkisel referans anayasasını tanımlar.

---

## 1. Gereksinim Düzeyleri ve Token Standartları

Sistem, token öneklerine (prefixes) göre 6 aşamalı V-Model hiyerarşisi oluşturur. Tüm tokenler `REQ_[DÜZEY]_[MODÜL]_[NUMARA]` veya `PBI_[NUMARA]` formatında olmalıdır.

| Seviye | Token Formatı | Açıklama | Örnek |
|--------|---------------|----------|-------|
| **L0 (Vision)** | `REQ_VD_XXX_00` | Vizyon Kısıtları & İş Kuralları | `[REQ_VD_TEC_01]` |
| **L1 (GDD)** | `REQ_GDD_XXX_00` | Oyun Tasarım Mekanikleri ve Matematiksel Modeller | `[REQ_GDD_SYS_01]` |
| **L2 (NDD)** | `REQ_NDD_XXX_00` | Anlatı & Görev Kurgusu | `[REQ_NDD_LOR_01]` |
| **L3-C (TDD)** | `REQ_TDD_XXX_00` | Teknik Mimari & Kodlama Kısıtları | `[REQ_TDD_LCM_01]` |
| **L3-D (ADD)** | `REQ_ADD_XXX_00` | Sanat Bütçeleri & Ses Kuralları | `[REQ_ADD_ANM_01]` |
| **L4 (PBI)** | `PBI_[0-9]+` | Çevik Sprint İş Paketleri (Product Backlog) | `[PBI_042]` |
| **L5 (QA)** | `TC_QA_XXX_PBIXXX_A` | Master Test Senaryoları | `[TC_QA_LCM_PBI001_A]` |

### Modül Kısaltmaları (XXX placeholders):
- **Genel (Generic):** `SYS` (System), `UI` (Interface), `GEN` (General)
- **Karakter & Kombat:** `LCM` (Locomotion), `CMB` (Combat), `AI` (Artificial Intelligence)
- **Kabile & Ekonomi:** `CML` (Camp Life/Tribe), `ECO` (Economy), `INV` (Inventory)
- **Hikaye & Bölüm:** `LOR` (Lore), `QST` (Quest), `LVL` (Level Design)
- **Sanat & Ses:** `TEX` (Texture), `ANM` (Animation), `AUD` (Audio), `VFX` (Visual Effects)

---

## 2. Tanımlama Kalıpları (3 Extraction Patterns)

AST Parser, markdown dosyalarındaki gereksinimleri 3 farklı sözdizimi yapısında algılar:

### Kalıp A: Tablo Satırı (Table Row)
En sık kullanılan ve yapılandırılmış alan içeren kalıptır. Tablonun ilk hücresinde token **kalın** yazılmalı, ikinci hücrede başlık, üçüncü hücrede açıklama yer almalıdır.
```markdown
| **[REQ_VD_TEC_01]** | Yükleme ve Başlatma Hızı | Oyun, High grafik ayarlarında 60 FPS stabil çalışmalıdır. |
```

### Kalıp B: Başlık (Heading)
Gereksinimin ana veya alt başlık olarak tanımlandığı durumlardır. Token, başlığın en sonunda köşeli parantez içinde yer almalıdır. Altındaki ilk 5 satır açıklama (description) olarak taranır.
```markdown
## 2.1. Kozmoloji [REQ_NDD_LOR_01]
Türk mitolojisindeki Altay yaradılış destanına dayanarak obanın göç yolları belirlenir...
```

### Kalıp C: Liste Öğesi (List Item)
Liste şeklinde hızlı gereksinim tanımları için kullanılır.
```markdown
* **[REQ_TDD_CMB_01]** Hitstop Süresi: Düşmana başarılı yakın dövüş darbesi yapıldığında dünya 50ms donmalıdır.
```

---

## 3. İzlenebilirlik ve Referans Standartları (Traceability Rules)

Gereksinimler arasındaki ilişkileri kurmak için 4 dikey entegrasyon yöntemi mevcuttur:

1. **Aynı Satırda Çoklu Token:** Bir tabloda veya satırda iki token aynı anda geçiyorsa, hiyerarşide üstte olan alttakine otomatik olarak bağlanır.
2. **Bağlam İzleme (Heading Context):** Bir gereksinim başlığı altında yazılan tüm diğer gereksinim tokenleri, o başlık gereksiniminin çocukları (`downstream`) olarak etiketlenir.
3. **Anahtar Kelime Referansı:** Satır içinde `Ref:`, `Referans:`, `İlgili PBI:`, `İlgili Gereksinim:`, `Bağlı L0 Kısıtı:` kalıplarını takip eden tokenler doğrudan ilişkilendirilir.
   ```markdown
   **İlgili İş Paketi Linki:** [PBI_001]
   ```
4. **Ön Koşul Blokları:** Düğüm başlığının hemen altında yer alan `Giriş Ön Koşulları` veya `Ön Koşul` alt başlığı altındaki liste tokenleri upstream bağımlılık olarak taranır.

---

## 4. Git Commit ve Branch Standartları

ALM sisteminin PBI ve kod entegrasyonunu (dikey izlenebilirlik) denetleyebilmesi için Git işlemlerinde şu kurallar zorunludur:

### Commit Mesaj Formatı:
Her commit mesajının başında sürüm kodu, ardından köşeli parantez içinde ilişkili `PBI_XXX` kimliği ve açıklamanın sonunda ilişkili gereksinim tokeni yer almalıdır:
```
v1.1:0 - [PBI_001] - Karakter temel yürüme ivmesi 600cm/s olarak optimize edildi [REQ_TDD_LCM_01]
```

### Branch İsimlendirme Formatı:
Dikey branch izlenebilirliği için branch adları iş paketleriyle eşleşmelidir:
```
feature/PBI_042-double-jump
bugfix/PBI_005-hitstop-freeze
```

---

## 5. Yeni Proje Ekleme Adımları (Checklist)

Yeni bir oyun veya yazılım projesini ALM portalına entegre etmek için:
1. `docs/ProjectDocuments/` klasörünün altında en az bir adet `.md` dosyasında Seviye 0 (`REQ_VD_*`) kısıtı tanımlayın.
2. Arayüz üzerindeki **"+ Add Project"** butonuna basarak proje ID'si, yerel kök dizini ve döküman klasör yollarını girin.
3. **"Refresh System"** butonuna basarak ilk AST taramasını gerçekleştirin.
4. Çevrimdışı matrisin ve Obsidian grafiğinin başarıyla üretildiğini doğrulayın.
