from .legalitas import extract_legalitas
from .tenaga_ahli import extract_tenaga_ahli
from .kontrak import extract_kontrak
from .cv import extract_cv
from .keuangan import extract_keuangan
from .surat_masuk import extract_surat_masuk
from .surat_keluar import extract_surat_keluar
from .pengurus_pemegang_saham import extract_pengurus_pemegang_saham

__all__ = [
    "extract_legalitas",
    "extract_tenaga_ahli",
    "extract_kontrak",
    "extract_cv",
    "extract_keuangan",
    "extract_surat_masuk",
    "extract_surat_keluar",
    "extract_pengurus_pemegang_saham"
]
