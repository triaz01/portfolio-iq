import os
import sys
import base64
import logging
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse, ORJSONResponse

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Configure logging
import datetime

# Setup comprehensive file logging
LOG_FILE = "debug_log.txt"

def log_step(step, details=None):
    """Write detailed logs to file for debugging"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_entry = f"[{timestamp}] {step}"
    if details:
        log_entry += f" | {details}"
    
    # Always write to file, never fail
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
            f.flush()  # Force write immediately
    except Exception as e:
        # If logging fails, at least try to write the error
        try:
            with open("logging_error.txt", "a", encoding="utf-8") as f:
                f.write(f"Failed to log: {e}\n")
        except:
            pass

# Initialize log file - append mode to preserve previous entries
try:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*80}\n")
        f.write(f"=== Backend Server Started at {datetime.datetime.now()} ===\n")
        f.write(f"{'='*80}\n")
except:
    pass

log_step("STARTUP", "Loading environment and modules")

load_dotenv()

log_step("STARTUP", "Importing logic modules")

from logic.extractor import parse_pasted_text, parse_csv_dataframe
from logic.ips_engine import calculate_ips, assess_alignment, get_ips_targets
from logic.metrics import (
    calculate_portfolio_metrics,
    generate_investor_summary,
    generate_trading_signals
)
from logic.monte_carlo import run_monte_carlo
from logic.pdf_generator import generate_pdf_report

log_step("STARTUP", "All modules imported successfully")

app = FastAPI(title="PortfolioIQ API", version="1.0.0")

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request Models ──────────────────────────────

class IPSRequest(BaseModel):
    time_horizon: int
    liquidity: str
    objective: str
    crash_reaction: str
    knowledge: str

class AnalyzeRequest(BaseModel):
    text: str
    currency: str = "CAD"

class AlignmentRequest(BaseModel):
    metrics: dict
    ips_targets: dict
    ips_profile: str

class MonteCarloRequest(BaseModel):
    initial_value: float
    cagr: float
    volatility: float
    years: int = 20
    simulations: int = 500
    annual_withdrawal: float = 0

class PDFRequest(BaseModel):
    metrics: dict = {}
    ips_profile: str = ""
    ips_alignment_bullets: list = []
    ips_targets: dict = {}
    projection_df_json: list = []
    correlation_matrix: dict = {}
    chart_data: dict = {}
    signals: list = []
    monte_carlo_data: dict = {}
    currency: str = "CAD"
    mc_years: int = 20
    mc_withdrawal: float = 0

class SignalsRequest(BaseModel):
    tickers: list[str]

# ── Routes ─────────────────────────────────────

@app.get("/")
def health():
    return {"status": "ok", "service": "PortfolioIQ API"}

@app.get("/test")
def test():
    """Simple test endpoint to verify server is working"""
    from logic.extractor import parse_pasted_text
    from logic.metrics import calculate_portfolio_metrics
    
    portfolio = parse_pasted_text("AAPL 100")
    metrics = calculate_portfolio_metrics(portfolio, "CAD")
    
    if metrics:
        # Remove DataFrames before returning
        if 'projection_df' in metrics:
            del metrics['projection_df']
        if 'correlation_matrix' in metrics:
            del metrics['correlation_matrix']
        if 'chart_data' in metrics:
            del metrics['chart_data']
        return {"success": True, "portfolio_value": metrics.get('total_value')}
    return {"success": False}

@app.post("/api/ips")
def generate_ips(req: IPSRequest):
    try:
        log_step("IPS_REQUEST_START", f"time_horizon={req.time_horizon}, liquidity={req.liquidity}, objective={req.objective}")
        
        profile, targets = calculate_ips(
            req.time_horizon,
            req.liquidity,
            req.objective,
            req.crash_reaction,
            req.knowledge
        )
        
        log_step("IPS_CALCULATION_SUCCESS", f"profile_type={profile}, targets_count={len(targets) if targets else 0}")
        
        return {"profile": profile, "targets": targets}
    except Exception as e:
        log_step("IPS_ERROR", f"error={str(e)}")
        import traceback
        log_step("IPS_TRACEBACK", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
def analyze_portfolio(req: AnalyzeRequest):
    import io
    import contextlib
    
    try:
        log_step("ANALYZE_REQUEST_START", f"text_length={len(req.text)}, currency={req.currency}")
        
        # Suppress all print output to prevent encoding errors
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            portfolio = parse_pasted_text(req.text)
        
        log_step("PARSING_COMPLETE", f"portfolio={portfolio}")
        
        if not portfolio:
            log_step("PARSING_FAILED", "No valid tickers found")
            raise HTTPException(
                status_code=400,
                detail="No valid tickers found. Check your input format."
            )
        
        log_step("METRICS_CALCULATION_START", f"tickers={list(portfolio.keys())}")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            metrics = calculate_portfolio_metrics(portfolio, req.currency)
        
        log_step("METRICS_CALCULATION_COMPLETE", f"metrics_available={metrics is not None}")
        
        if metrics is None:
            log_step("METRICS_FAILED", "calculate_portfolio_metrics returned None")
            raise HTTPException(
                status_code=400,
                detail="Unable to fetch data. Verify ticker symbols."
            )
        
        log_step("SUMMARY_GENERATION_START")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            summary = generate_investor_summary(metrics)
        
        log_step("SUMMARY_GENERATION_COMPLETE", f"summary_length={len(summary) if summary else 0}")
        
        import numpy as np
        import pandas as pd

        # Convert projection_df to JSON-serializable format
        log_step("JSON_CONVERSION_START", "Converting projection_df")
        proj_json = None
        if 'projection_df' in metrics and metrics['projection_df'] is not None:
            proj_df = metrics['projection_df'].replace([np.inf, -np.inf], np.nan)
            proj_df = proj_df.astype(object).where(pd.notna(proj_df), None)
            proj_json = proj_df.to_dict(orient='records')
            del metrics['projection_df']
            log_step("JSON_CONVERSION_SUCCESS", f"projection_df converted, {len(proj_json)} records")
        
        # Convert correlation_matrix to JSON-serializable format  
        log_step("JSON_CONVERSION_START", "Converting correlation_matrix")
        corr_json = None
        if 'correlation_matrix' in metrics and metrics['correlation_matrix'] is not None:
            corr_df = metrics['correlation_matrix'].replace([np.inf, -np.inf], np.nan)
            corr_df = corr_df.astype(object).where(pd.notna(corr_df), None)
            corr_json = corr_df.to_dict()
            del metrics['correlation_matrix']
            log_step("JSON_CONVERSION_SUCCESS", "correlation_matrix converted")
        
        # Convert chart_data to JSON-serializable format
        log_step("JSON_CONVERSION_START", "Converting chart_data")
        chart_json = None
        if 'chart_data' in metrics and metrics['chart_data'] is not None:
            chart_df = metrics['chart_data'].replace([np.inf, -np.inf], np.nan)
            chart_df = chart_df.astype(object).where(pd.notna(chart_df), None)
            chart_df.index = chart_df.index.astype(str)
            chart_json = chart_df.to_dict(orient='index')
            del metrics['chart_data']
            log_step("JSON_CONVERSION_SUCCESS", f"chart_data converted, {len(chart_json)} rows")
        
        log_step("RESPONSE_BUILD_START", "Building final response")
        
        # Clean metrics dictionary - convert all numpy/pandas types to native Python types
        def clean_value(obj):
            """Recursively convert numpy/pandas types to JSON-safe native Python types."""
            import math

            if obj is None:
                return None

            if isinstance(obj, (np.integer,)):
                return int(obj)

            if isinstance(obj, (np.floating, float)):
                val = float(obj)
                return val if math.isfinite(val) else None

            if isinstance(obj, np.ndarray):
                return clean_value(obj.tolist())

            if isinstance(obj, dict):
                return {k: clean_value(v) for k, v in obj.items()}

            if isinstance(obj, (list, tuple)):
                return [clean_value(item) for item in obj]

            if isinstance(obj, (str, int, bool)):
                return obj

            return str(obj)
        
        cleaned_metrics = clean_value(metrics)
        cleaned_summary = clean_value(summary)
        cleaned_proj_json = clean_value(proj_json)
        cleaned_corr_json = clean_value(corr_json)
        cleaned_chart_json = clean_value(chart_json)
        
        log_step("RESPONSE_BUILD_START", "Building final response")
        
        # Return the complete portfolio analysis response
        response = {
            "success": True, 
            "message": "Analysis complete", 
            "metrics": cleaned_metrics,
            "summary": cleaned_summary,
            "projection_df": cleaned_proj_json,
            "chart_data": cleaned_chart_json,
            "correlation_matrix": cleaned_corr_json
        }
        log_step("RESPONSE_BUILD_SUCCESS", "Response ready to return")
        log_step("FINAL_RESPONSE", f"Returning complete analysis with {len(str(response))} bytes")
        
        return ORJSONResponse(content=response)
    except HTTPException:
        raise
    except Exception as e:
        error_details = traceback.format_exc()
        logging.error(f"\n[API ERROR] Exception occurred: {error_details}")
        
        # Write detailed error to file for debugging
        try:
            with open("analyze_error.log", "w", encoding="utf-8") as f:
                f.write(f"Error Time: {__import__('datetime').datetime.now()}\n")
                f.write(f"Error Type: {type(e).__name__}\n")
                f.write(f"Error Message: {str(e)}\n")
                f.write(f"\nFull Traceback:\n{error_details}\n")
        except:
            pass
        
        # Try to get a safe error message
        try:
            error_msg = str(e)
        except:
            error_msg = "Unknown error occurred"
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/signals")
def get_signals(req: SignalsRequest):
    try:
        signals_df = generate_trading_signals(req.tickers)
        return {"signals": signals_df.to_dict(orient='records')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/alignment")
def check_alignment(req: AlignmentRequest):
    try:
        result = assess_alignment(
            req.metrics,
            req.ips_targets,
            req.ips_profile
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/montecarlo")
def monte_carlo(req: MonteCarloRequest):
    try:
        mc_df = run_monte_carlo(
            initial_value=req.initial_value,
            cagr=req.cagr,
            volatility=req.volatility,
            years=req.years,
            simulations=req.simulations,
            annual_withdrawal=req.annual_withdrawal
        )
        mc_df.index = mc_df.index.astype(float).round(4)
        return {"data": mc_df.to_dict(orient='index')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pdf")
def generate_pdf(req: PDFRequest):
    try:
        import pandas as pd
        import json
        
        log_step("PDF_REQUEST_START", f"Generating PDF with {len(req.projection_df_json) if req.projection_df_json else 0} projections")
        
        # Handle projection_df_json - it might be a string or already a list
        try:
            if isinstance(req.projection_df_json, str):
                proj_data = json.loads(req.projection_df_json)
            else:
                proj_data = req.projection_df_json
            
            proj_df = pd.DataFrame(proj_data)
            log_step("PDF_PROJECTIONS_SUCCESS", f"Created DataFrame with {len(proj_df)} rows")
        except Exception as df_error:
            log_step("PDF_PROJECTIONS_ERROR", f"DataFrame creation failed: {str(df_error)}")
            # Create empty DataFrame as fallback
            proj_df = pd.DataFrame()
        
        # Create Monte Carlo chart from frontend data
        monte_carlo_fig = None
        try:
            if req.monte_carlo_data and isinstance(req.monte_carlo_data, dict):
                from logic.pdf_generator import create_monte_carlo_chart
                
                # Use the exact Monte Carlo data from frontend
                monte_carlo_fig = create_monte_carlo_chart(req.monte_carlo_data)
                log_step("PDF_MONTECARLO_SUCCESS", "Monte Carlo chart created from frontend data")
        except Exception as mc_error:
            log_step("PDF_MONTECARLO_ERROR", f"Monte Carlo chart creation failed: {str(mc_error)}")
        
        pdf_bytes = generate_pdf_report(
            metrics=req.metrics,
            ips_profile=req.ips_profile,
            ips_alignment_text=req.ips_alignment_bullets,
            growth_chart_fig=None,
            projection_df=proj_df,
            ips_targets=req.ips_targets,
            monte_carlo_fig=monte_carlo_fig,
            correlation_matrix=req.correlation_matrix,
            chart_data=req.chart_data,
            signals=req.signals,
            currency=req.currency,
            mc_years=req.mc_years,
            mc_withdrawal=req.mc_withdrawal
        )
        
        log_step("PDF_GENERATION_SUCCESS", "PDF generated successfully")
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 
                    "attachment; filename=portfolio_report.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        log_step("PDF_ERROR", f"PDF generation failed: {str(e)}")
        # Write to log file for debugging
        try:
            with open("api_error.log", "a", encoding="utf-8") as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Timestamp: {__import__('datetime').datetime.now()}\n")
                f.write(error_msg)
                f.write(f"\n{'='*50}\n")
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/signals")
def get_signals(req: SignalsRequest):
    try:
        signals_df = generate_trading_signals(req.tickers)
        return {"signals": signals_df.to_dict(orient='records')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/alignment")
def check_alignment(req: AlignmentRequest):
    try:
        result = assess_alignment(
            req.metrics,
            req.ips_targets,
            req.ips_profile
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/montecarlo")
def monte_carlo(req: MonteCarloRequest):
    try:
        mc_df = run_monte_carlo(
            initial_value=req.initial_value,
            cagr=req.cagr,
            volatility=req.volatility,
            years=req.years,
            simulations=req.simulations,
            annual_withdrawal=req.annual_withdrawal
        )
        mc_df.index = mc_df.index.astype(float).round(4)
        return {"data": mc_df.to_dict(orient='index')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))