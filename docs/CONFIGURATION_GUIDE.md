# Ludus Magnus ALM — Proje Yapılandırma Rehberi (CONFIGURATION_GUIDE.md)

Bu rehber, Ludus Magnus ALM sisteminin projects.json şemasını, baseline snapshot mekanizmasını, CLI parametrelerini ve online/offline çalışma modlarının yapılandırma detaylarını açıklamaktadır.

---

## 1. CLI Parametreleri ve Sunucu Yönetimi

ALM orchestrator'ı (`alm_orchestrator.py`), Python standart kütüphanesini kullanarak hem bir CLI aracı hem de hafif bir web sunucusu olarak çalışır.

### Kullanım Komutları:

#### A. Web Portalı Sunucusunu Başlatma:
Varsayılan olarak 8002 portunda sunucuyu çalıştırır ve `alm_portal.html` arayüzünü tarayıcıya sunar.
```powershell
python alm_orchestrator.py --serve
```
*Port 8002 meşgulse sunucu otomatik olarak 8003, 8004... portlarına düşerek çalışmaya devam eder.*

#### B. Özel Port Belirtme:
```powershell
python alm_orchestrator.py --serve --port 8085
```

#### C. Sadece Gereksinim Taraması Yapma (Scan-Only):
Sunucuyu açmadan tüm projeleri tarar, ilişkisel bağlantı doğrulamalarını gerçekleştirir ve offline arayüzün okuması için static JSON çıktılarını `_LM_ALM_System/alm_offline_data/` dizinine ihraç eder.
```powershell
python alm_orchestrator.py --scan
```

#### D. Sürüm Dondurma ve Baseline Snapshot Oluşturma:
```powershell
python alm_orchestrator.py --baseline "Sprint_2_Kapanis"
```

---

## 2. projects.json Şeması ve Proje Ekleme

ALM sistemi çoklu proje (multi-project) mimarisine sahiptir. Konfigürasyonlar kök dizindeki `projects.json` dosyasında saklanır:

```json
{
  "projects": [
    {
      "id": "ProjectCult",
      "name": "Project Cult",
      "local_root": "C:/repo/3_UE5_ProjectCult/",
      "docs_path": "C:/repo/3_UE5_ProjectCult/docs/ProjectDocuments/",
      "rules_path": "C:/repo/3_UE5_ProjectCult/docs/Standarts/",
      "github_url": "",
      "last_scan": "2026-05-31T17:45:00",
      "created_at": "2026-05-31T17:45:00"
    }
  ]
}
```

### Konfigürasyon Alanları:
- `id`: Benzersiz proje kimliği (Boşluksuz ve İngilizce karakter).
- `name`: Arayüzde görüntülenecek estetik proje adı.
- `local_root`: Projenin Git geçmişini okumak için taranacak yerel Git kök klasörü.
- `docs_path`: Gereksinim markdown (.md) dosyalarının bulunduğu döküman klasörü.
- `rules_path`: ASPICE veya kodlama yönergelerinin yer aldığı standartlar klasörü.

---

## 3. Baseline Snapshot / Dondurulmuş Sürümler

Release öncesi gereksinim ağacını korumak ve iki sürüm arasındaki eklenen/silinen/değişen maddeleri listelemek amacıyla Baseline modülü kullanılır.

- **Dosya Yolu:** Üretilen baseline snapshot'ları `baselines/{project_id}/{tarih_saat}.json` olarak JSON formatında kaydedilir.
- **Karşılaştırma (Comparison):** Arayüz üzerindeki **Sprint Paneli (Tab 7)** altından dilediğiniz iki dondurulmuş baseline snapshot'ını seçerek, iki sürüm arasındaki gereksinim mutasyonlarını (Mutation Diff) görebilirsiniz.

---

## 4. Online / Offline Mod Çalışma Politikası

Ludus Magnus ALM portalı, internet ve sunucu bağımsız her koşulda çalışabilecek şekilde tasarlanmıştır.

### Offline Mod:
`_LM_ALM_System/alm_portal.html` dosyasına çift tıklayarak tarayıcıda doğrudan açtığınızda devreye girer.
- Verileri `alm_offline_data/{project_id}.json` yerel dosyasından okur.
- Ağ grafiği, Obsidian görünümü, kapsam matrisi ve etki analizleri tamamen offline ve yerel olarak çalışır.
- Gitcommit senkronizasyonu statik cache verilerini kullanır.

### Online Mod:
Kök dizindeki `run_alm.bat` başlatıcısını çalıştırdığınızda veya sunucuyu `--serve` ile ayağa kaldırdığınızda aktif olur.
- Gerçek zamanlı Git logları, commit-gereksinim ilişkileri anlık taranır.
- Sistem üzerinde anlık yenileme (Refresh) ve yeni Baseline oluşturma özellikleri açılır.
- Arayüz üzerinden dinamik olarak yeni projeler import edilebilir.
