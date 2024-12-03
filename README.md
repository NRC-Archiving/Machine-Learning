# Machine-Learning
Repository ini berisi proyek pengembangan model amchine learning yang digunakan pada pengembangan Aplikasi Arsip Digital di PT Nusa Raya Cipta Tbk.

Model Machine Learning yang digunakan ada dua
# 1. Model OCR dengan integrasi REGEX

Model OCR digunakan untuk melakukan ekstraksi teks yang ada pada dokumen. Ekstraksi teks kemudian diproses dengan konfigurasi REGEX tertentu untuk mengambil frasa-frasa tertentu sesuai yang dibutuhkan untuk tiap jenis doukmen yang ada. 

# 2. Model NLP

Model NLP digunakan untuk melakukan penerjemahan dokumen dari yang awalnya menggunakan Bahasa Indonesia menjadi Bahasa Inggris.

# 3. System Dependencies

Untuk menggunakan aplikasi, dibutuhkan beberapa system dependency sebagai berikut

1.) tesseract-ocr : digunakan untuk menjalankan fungsi pada library tesseract
2.) poppler-utils : digunakan untuk menjalankan fungsi pada pdf2image
3.) libsm6, libxext6, libxrender-dev, libglib2.0-0 : digunakan untuk menjalankan berbagai fungsi dalam library opencv