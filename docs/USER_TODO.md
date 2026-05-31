# Ludus Magnus ALM — Kullanıcı Operasyon ve Test Kılavuzu (USER_TODO.md)

Bu döküman, ALM sisteminin kurulumunu tamamladıktan sonra sistemin tüm sekmelerini test etmeniz, sunucuyu ayağa kaldırmanız ve dikey entegrasyonu denetlemeniz için yapmanız gereken adımları içerir.

---

## ADIM 1: Sistemi Çift Tıklama ile Başlatma

Sistemin tüm Git senkronizasyonu ve dinamik özellikleriyle (Online Mode) çalışabilmesi için sunucunun aktif olması gerekir.

1. Proje kök dizininde yer alan `run_alm.bat` dosyasına çift tıklayın.
2. Bu dosya, arka planda Python sunucusunu 8002 portunda başlatacak ve varsayılan internet tarayıcınızda otomatik olarak portal arayüzünü (`http://localhost:8002/`) açacaktır.
3. **Doğrulama:** Arayüzün sol üst köşesindeki yeşil **"Online Mod"** rozetinin yandığını kontrol edin.

---

## ADIM 2: İlk Taramayı (Refresh) Gerçekleştirme

Varsayılan `ProjectCult` projesinin dökümanlarının taranıp veri tabanına işlenmesi için:

1. Arayüzün sağ üst köşesinde yer alan **"🔄 Refresh System"** butonuna basın.
2. Ekranda taramanın başarıyla tamamlandığına dair bildirim belirecektir.
3. **Doküman Gezgini (Tab 1)** sekmesine gelerek `VD.md` veya `GDD.md` sekmelerine tıklayın. Gereksinimlerin listelendiğini doğrulayın.

---

## ADIM 3: Git Commit ve PBI Entegrasyonunu Senkronize Etme

Commit geçmişindeki gereksinim/PBI eşleştirmelerini test etmek için:

1. Sağ üst köşedeki **"📡 Sync Git"** butonuna basın.
2. En sağdaki **Sprint Paneli (Tab 7)** sekmesine geçiş yapın.
3. Sağ alt köşedeki **"Son Git Commitleri"** zaman çizelgesinde son commitlerin listelendiğini ve commit mesajlarındaki `PBI_XXX` ve `[REQ_*]` etiketlerinin otomatik taranıp yeşil/mavi rozetlerle etiketlendiğini doğrulayın.

---

## ADIM 4: Manuel Gereksinim Ekleme (Override Testi)

Eğer otomatik parse dışında elinizle manuel gereksinim veya ilişkisel bağ eklemek isterseniz:

1. `C:\repo\3_UE5_ProjectCult\docs\ProjectDocuments\` dizininin altında **`manual_requirements.json`** adında bir dosya oluşturun ve içine şu örnek veriyi ekleyin:
   ```json
   {
     "REQ_VD_TEC_99": {
       "title": "Manuel Tanımlanmış Optimizasyon Hedefi",
       "desc": "Bu gereksinim kullanıcı arayüzü ve testler için manuel eklenmiştir."
     }
   }
   ```
2. Aynı dizinde **`manual_edges.json`** adında bir dosya oluşturarak bu manuel gereksinimi `REQ_GDD_SYS_01` düğümüne bağlayın:
   ```json
   [
     {
       "source": "REQ_VD_TEC_99",
       "target": "REQ_GDD_SYS_01",
       "type": "manual"
     }
   ]
   ```
3. Arayüzden tekrar **"🔄 Refresh System"** butonuna basın. Matris ve ağ üzerinde manuel gereksinimin başarıyla eklendiğini ve otomatik gereksinimlerle birleştirildiğini (merge) gözlemleyin.
