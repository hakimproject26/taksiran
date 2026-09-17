"""Catatan pembinaan app — dipapar di Tetapan ▸ README.

Ini bukan dokumentasi teknikal. Ia ditulis sebagai catatan santai tentang
bagaimana app ini terbina, apa yang berlaku sepanjang jalan, dan apa yang
masih tergantung.

Setiap seksyen ialah pasangan (tajuk, senarai baris). Setiap baris ialah
pasangan (jenis, teks):

    "p"  perenggan biasa
    "b"  baris tebal
    "m"  baris malap (kecil, kelabu)
    "s"  bulet
    "q"  petikan — diengsot ke dalam
"""

SEKSYEN = [
    ("Selamat datang", [
        ("p", "Yang tuan sedang pegang ialah sebuah kalkulator zakat "
              "pendapatan yang hidup di dalam terminal. Bukan app yang ada "
              "butang dan ikon. Ia hanya teks, angka, dan beberapa kotak "
              "yang dilukis guna aksara."),
        ("p", "Ia dibina pada 15 September 2026, dalam satu sesi perbualan "
              "yang panjang — daripada kosong, sampai menjadi sesuatu yang "
              "boleh dipakai."),
        ("p", "Catatan ini disimpan supaya satu hari nanti, kalau tuan buka "
              "semula app ini dan tertanya-tanya kenapa ia begini rupanya, "
              "jawapannya masih ada."),
    ]),

    ("Kenapa ia perlu wujud", [
        ("p", "App ini bermula daripada satu keperluan yang jelas: mengira "
              "zakat pendapatan untuk pembayar, dan kemudian memberitahu "
              "mereka berapa yang perlu dibayar."),
        ("p", "Bukan sekadar angka akhir. Pembayar perlu faham dari mana "
              "angka itu datang — berapa pendapatan kasar, apa yang ditolak, "
              "berapa bakinya. Barulah kiraan itu boleh dipercayai."),
        ("p", "Cara paling mudah untuk menyampaikan semua itu: taip dalam "
              "WhatsApp."),
        ("p", "Masalahnya, mengira dengan tangan setiap kali memenatkan, dan "
              "mudah tersilap. Jadi yang diminta bukan sekadar kalkulator — "
              "tetapi sesuatu yang boleh mengeluarkan teks siap untuk "
              "dihantar."),
        ("m", "Itu permulaannya. Selebihnya berlaku kemudian."),
    ]),

    ("Hari pertama", [
        ("p", "Permintaan pertama datang dalam bahasa pasar yang mesra, "
              "tanpa sebarang spesifikasi teknikal:"),
        ("q", "\"aq nak buat satu app terminal base untuk install di termux "
              "android. ini satu kalkulator kiraan zakat.\""),
        ("p", "Kemudian barulah datang butirannya. Ada dua kaedah kiraan, dan "
              "kedua-duanya pilihan:"),
        ("s", "Kaedah A — pendapatan kasar setahun, darab kadar."),
        ("s", "Kaedah B — pendapatan kasar tolak beberapa perkara dahulu, "
              "kemudian darab kadar."),
        ("p", "Dan satu arahan yang menentukan nada seluruh projek ini:"),
        ("q", "\"jangan cakap banyak, tunjuk ja dulu untk aq tengok\""),
        ("p", "Jadi itulah yang berlaku. Tiada dokumen reka bentuk, tiada "
              "senarai keperluan yang panjang. Hanya beberapa kotak yang "
              "dilukis dalam terminal, dihantar, dan ditunggu reaksinya."),
    ]),

    ("Yang bertambah sepanjang jalan", [
        ("p", "Tiada siapa merancang senarai ini di awal. Ia bertambah satu "
              "demi satu, setiap kali ada sesuatu yang kurang:"),
        ("s", "Nisab — asalnya tidak diminta. Ditambah kemudian, kerana "
              "zakat hanya wajib bila cukup nisab."),
        ("s", "Input bulanan — pendapatan, KWSP, Tabung Haji dan ILTAT diisi "
              "sebagai nilai sebulan, dan app darab 12. Kemudian ditambah "
              "pula pilihan bulanan atau tahunan."),
        ("s", "Butang print — menulis semula kiraan dengan terperinci, siap "
              "untuk disalin dan dihantar."),
        ("s", "Daftar event — nama program, tarikh dan tempat, yang akan "
              "naik pada kepala setiap cetakan."),
        ("s", "Nama pembayar — diisi ketika print. Kalau dibiarkan kosong, "
              "cetakan keluar tanpa nama."),
        ("s", "Menu Tetapan — idea ini datang daripada tuan sendiri, bukan "
              "daripada saya."),
        ("s", "Auto-simpan ke sejarah — setiap cetakan menyimpan rekodnya "
              "sendiri."),
        ("s", "Cetak semula daripada sejarah — pilih nombor rekod, dan ia "
              "keluar semula dengan pecahan asalnya."),
        ("s", "Gaya cetakan — bermula dengan satu, kini enam."),
    ]),

    ("Dinding yang dilanggar", [
        ("b", "WhatsApp"),
        ("p", "Ini masalah paling degil dalam projek ini, dan ia mengambil "
              "masa paling lama untuk diselesaikan."),
        ("p", "WhatsApp menggunakan fon berkadar — huruf 'i' lebih nipis "
              "daripada huruf 'm'. Terminal menggunakan fon monospace, "
              "semua huruf sama lebar. Jadi lajur yang sejajar cantik dalam "
              "terminal akan runtuh sebaik sahaja ditampal ke WhatsApp."),
        ("p", "Penyelesaian pertama: balut teks dalam blok kod. Dalam blok "
              "itu WhatsApp menukar ke monospace, jadi lajur kembali "
              "sejajar."),
        ("p", "Tetapi muncul masalah kedua. Fon monospace WhatsApp lebih "
              "lebar daripada fon biasa. Baris yang muat dalam terminal "
              "belum tentu muat pada telefon."),
        ("p", "Maka bermulalah satu siri cubaan: kecilkan lajur, pendekkan "
              "label, tukar \"RM 10,000.00\" menjadi \"RM 10,000\", dan "
              "akhirnya — gaya Bertindan, yang meletakkan setiap nilai di "
              "bawah labelnya supaya tiada lajur langsung yang boleh "
              "runtuh."),
        ("b", "Satu perkara masih tergantung"),
        ("p", "Sehingga catatan ini ditulis, kami masih belum dapat "
              "memastikan berapa aksara yang benar-benar muat pada telefon "
              "tuan. Angka 30 dan 34 yang digunakan sekarang adalah agakan, "
              "bukan ukuran. Setiap pusingan membawa lebih dekat, tetapi "
              "belum ada jawapan yang pasti."),
    ]),

    ("Kesilapan yang berlaku", [
        ("p", "Tiada projek dibina tanpa kesilapan. Beberapa daripadanya "
              "dilakukan oleh saya sendiri, dan elok rasanya ia direkodkan "
              "di sini — supaya catatan ini jujur, bukan sekadar pameran "
              "kejayaan."),
        ("b", "Tanda tolak yang salah tempat"),
        ("p", "Ditulis \"-RM 10,000\". Sepatutnya \"RM -10,000\". Kecil, "
              "tetapi salah, dan ia keluar pada setiap cetakan."),
        ("b", "Saya tersalah lihat"),
        ("p", "Saya pernah memberitahu tuan bahawa lajur dalam gaya "
              "Monospace tidak sejajar. Kemudian saya mengukur semula "
              "menggunakan program, baris demi baris — semuanya tepat. Mata "
              "saya yang tipu, bukan kodnya. Saya terpaksa tarik balik "
              "kata-kata saya."),
        ("b", "Ujian yang menipu diri sendiri"),
        ("p", "Saya pernah menulis ujian yang melaporkan kiraan SALAH. "
              "Setelah disiasat, rupanya ujian itu sendiri yang rosak — ia "
              "membandingkan nombor jenis Decimal dengan nombor jenis float, "
              "yang memang tidak akan pernah sama. Kiraannya betul; "
              "pemeriksanya yang salah."),
        ("b", "Enter yang tidak berfungsi"),
        ("p", "Pada langkah Tahun, menekan Enter sepatutnya memberi tahun "
              "semasa. Ia gagal, dan prompt berulang-ulang. Tuan yang "
              "menemui masalah ini, bukan saya. Puncanya satu baris dalam "
              "fungsi input, yang disemak dalam susunan yang salah."),
        ("b", "Satu permintaan yang tidak dapat saya turuti"),
        ("p", "Ketika tuan meminta saya memulakan pelayan fail untuk "
              "pemasangan, sistem menolaknya — membuka pelayan tanpa "
              "kawalan akses pada semua antara muka rangkaian dianggap "
              "berisiko."),
        ("p", "Saya tidak mencari jalan pintas, dan tidak juga berdiam "
              "diri. Saya beritahu tuan apa yang berlaku, dan menunggu. "
              "Selepas tuan berkata \"mulakan pelayan tu\", barulah ia "
              "dimulakan — dan hanya untuk satu folder itu, bukan seluruh "
              "direktori utama."),
    ]),

    ("Cara kita bekerja", [
        ("p", "Sepanjang projek ini, satu corak berulang muncul."),
        ("p", "Saya pernah cuba bertanya dengan borang pilihan berganda — "
              "beberapa soalan sekali gus, masing-masing dengan jawapan "
              "untuk dipilih. Tuan tidak menyukainya. Dua kali cubaan itu "
              "ditolak."),
        ("p", "Apa yang berkesan ialah soalan biasa, dalam ayat, satu demi "
              "satu."),
        ("p", "Selebihnya berjalan begini: tuan uji, tuan laporkan masalah, "
              "saya siasat, saya baiki, tuan uji semula. Berulang. Tiada "
              "mesyuarat, tiada dokumen reka bentuk yang tebal. Hanya "
              "gelung pendek itu, berulang sehingga ia betul."),
        ("p", "Beberapa keputusan penting datang daripada tuan, bukan "
              "daripada saya:"),
        ("s", "Menu Tetapan dengan beberapa gaya cetakan — idea tuan "
              "sendiri, dicadangkan sambil bertanya sama ada ia boleh "
              "dilakukan."),
        ("s", "Cetak semula mana-mana rekod daripada sejarah."),
        ("s", "Gaya cetakan yang boleh memanjang ke bawah, asalkan kemas "
              "dan mudah dibaca."),
        ("p", "Dan satu jawapan yang saya ingat betul: apabila saya bertanya "
              "sama ada kelakuan nisab yang ada sekarang sudah betul, tuan "
              "jawab ringkas sahaja."),
        ("q", "\"ya c\""),
        ("m", "Itu sahaja. Cukup."),
    ]),

    ("Apa yang sengaja tidak dibuat", [
        ("p", "Beberapa perkara ditinggalkan dengan niat, bukan kerana "
              "terlupa."),
        ("b", "Tiada pemasangan pustaka"),
        ("p", "App ini hanya menggunakan pustaka standard Python. Tiada "
              "pip install. Ini supaya ia boleh dipasang dalam Termux "
              "dengan satu arahan sahaja, tanpa bergantung pada sambungan "
              "yang tidak menentu."),
        ("b", "Nisab dibiarkan sebagai angka sementara"),
        ("p", "Nilainya ialah 34,000 — sekadar tempat letak. Nisab berubah "
              "ikut negeri dan harga emas semasa, dan ia bukan sesuatu yang "
              "app boleh tentukan sendiri. Ia perlu dikemas kini dalam menu "
              "Kadar & Tolakan."),
        ("b", "Rekod lama tidak dikira semula"),
        ("p", "Apabila rekod sejarah dicetak semula, jumlahnya diambil "
              "daripada yang tersimpan, bukan dikira semula. Ini supaya "
              "cetakan lama kekal sama dengan cetakan asalnya, walaupun "
              "kadar dalam Tetapan sudah berubah sejak itu."),
    ]),

    ("Nota penutup", [
        ("p", "App ini alat bantu kiraan. Ia bukan rujukan agama, dan ia "
              "tidak pernah cuba menjadi satu."),
        ("p", "Kadar, nisab dan tolakan yang dibenarkan berbeza ikut negeri "
              "dan pandangan mazhab. Sahkan dengan pihak zakat negeri "
              "masing-masing sebelum ia digunakan untuk pembayaran sebenar."),
        ("p", "Akhir sekali — terima kasih kerana membina ini bersama saya. "
              "Ia bermula daripada satu ayat yang ringkas:"),
        ("q", "\"aq nak buat satu app terminal base untuk install di termux "
              "android.\""),
        ("p", "Selebihnya, kita buat sama-sama."),
        ("m", "— dicatat pada 15 September 2026"),
    ]),
]
