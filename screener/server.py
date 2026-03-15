"""
Integrated server for Clinical Spell Screener.
Serves the web UI at / and the MLM scoring API at /api/*.
"""

import argparse
import logging
import os
import sys
import webbrowser
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"


def create_app(model_name: Optional[str] = None, device: str = "auto") -> FastAPI:
    """
    Create the FastAPI application.

    Args:
        model_name: HuggingFace model name/path. If None, runs in dictionary-only mode.
        device: PyTorch device string.
    """
    mode = "MLM-assisted" if model_name else "Dictionary-only"

    app = FastAPI(
        title="Clinical Spell Screener",
        description=f"Medical text spell screening tool ({mode} mode)",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Load model if requested ──────────────────────────────────────────
    mlm = None
    if model_name:
        try:
            from screener.mlm import ClinicalMLM
            mlm = ClinicalMLM(model_name, device)
        except ImportError:
            logger.error(
                "PyTorch/transformers not installed. "
                "Install with: pip install torch transformers\n"
                "Or run in dictionary-only mode: python -m screener --no-model"
            )
            sys.exit(1)

    # ── Schemas ──────────────────────────────────────────────────────────
    class CandidateInput(BaseModel):
        word: str
        dist: int = 1

    class PredictRequest(BaseModel):
        context_before: str = Field(..., description="Words before the OOV token")
        token: str = Field(..., description="The OOV token to evaluate")
        context_after: str = Field(..., description="Words after the OOV token")
        candidates: List[CandidateInput] = Field(default_factory=list)
        top_k: int = Field(default=15)

    class BatchPredictRequest(BaseModel):
        items: List[PredictRequest]

    # ── API Endpoints ────────────────────────────────────────────────────
    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "mode": "mlm" if mlm else "dictionary-only",
            "model": model_name or "none",
            "device": str(mlm.device) if mlm else "n/a",
            "vocab_size": len(mlm.tokenizer) if mlm else 0,
        }

    @app.post("/api/predict")
    def predict(req: PredictRequest):
        if not mlm:
            return {"error": "MLM model not loaded. Running in dictionary-only mode."}
        candidates = [{"word": c.word, "dist": c.dist} for c in req.candidates]
        return mlm.predict_for_oov(
            context_before=req.context_before,
            oov_token=req.token,
            context_after=req.context_after,
            candidates=candidates,
            top_k=req.top_k,
        )

    @app.post("/api/predict_batch")
    def predict_batch(req: BatchPredictRequest):
        if not mlm:
            return {"error": "MLM model not loaded."}
        results = []
        for item in req.items:
            candidates = [{"word": c.word, "dist": c.dist} for c in item.candidates]
            results.append(mlm.predict_for_oov(
                context_before=item.context_before,
                oov_token=item.token,
                context_after=item.context_after,
                candidates=candidates,
                top_k=item.top_k,
            ))
        return {"results": results}

    # ── Serve the UI ─────────────────────────────────────────────────────
    @app.get("/")
    def serve_ui():
        return FileResponse(STATIC_DIR / "index.html")

    return app


def main():
    parser = argparse.ArgumentParser(
        description="Clinical Spell Screener — Medical text spell screening tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m screener                          # Full mode (MLM + UI)
  python -m screener --no-model               # Dictionary-only (no GPU needed)
  python -m screener --model bert-base-uncased # Custom model
  python -m screener --device cpu --port 9000  # CPU mode, custom port
        """,
    )
    parser.add_argument(
        "--model", type=str,
        default="thomas-sounack/BioClinical-ModernBERT-base",
        help="HuggingFace model name or local path (default: BioClinical-ModernBERT-base)",
    )
    parser.add_argument(
        "--no-model", action="store_true",
        help="Run in dictionary-only mode (no PyTorch/GPU required)",
    )
    parser.add_argument("--device", type=str, default="auto", help="Device: auto, cpu, cuda")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Bind host")
    parser.add_argument("--port", type=int, default=8400, help="Bind port")
    parser.add_argument("--no-browser", action="store_true", help="Don't auto-open browser")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    model_name = None if args.no_model else args.model
    app = create_app(model_name=model_name, device=args.device)

    url = f"http://localhost:{args.port}"
    mode = "dictionary-only" if args.no_model else f"MLM ({args.model})"

    print()
    print("=" * 60)
    print("  Clinical Spell Screener")
    print("=" * 60)
    print(f"  Mode:     {mode}")
    print(f"  URL:      {url}")
    print(f"  API docs: {url}/docs")
    print()
    print("  Open the URL above in your browser.")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 60)
    print()

    if not args.no_browser:
        import threading
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    import uvicorn
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
