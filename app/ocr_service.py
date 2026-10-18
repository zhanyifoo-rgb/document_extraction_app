from functools import lru_cache
from pathlib import Path

from paddleocr import PaddleOCR


@lru_cache(maxsize=1)
def get_ocr_engine():
    return PaddleOCR(
        lang="en",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        enable_mkldnn=False,
    )


def extract_text(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ocr = get_ocr_engine()
    results = ocr.predict(str(path))

    lines = []

    for page_index, result in enumerate(results):
        texts = result.get("rec_texts", [])
        scores = result.get("rec_scores", [])
        boxes = result.get("rec_boxes", [])

        for i, text in enumerate(texts):
            score = float(scores[i]) if i < len(scores) else None

            box = None
            if i < len(boxes):
                box = boxes[i].tolist()

            lines.append({
                "page": page_index + 1,
                "text": str(text).strip(),
                "confidence": score,
                "box": box,
            })

    return {
        "filename": path.name,
        "text": "\n".join(line["text"] for line in lines),
        "lines": lines,
    }