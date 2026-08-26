// Precisa gerar exatamente o mesmo slug que prospector/search.py::_slugify
// (Python), já que é a mesma key usada nos objetos do R2.
// eslint-disable-next-line no-misleading-character-class -- range de marcas
// diacriticas combinantes (U+0300 a U+036F), usado pra strippar acento apos
// normalize("NFKD"), igual ao unicodedata.normalize + encode ascii do Python.
const COMBINING_MARKS = /[̀-ͯ]/g;

export function slugify(text: string): string {
  const ascii = text.normalize("NFKD").replace(COMBINING_MARKS, "");
  return ascii
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}
