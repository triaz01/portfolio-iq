"""
Reusable HTML component builders.
All functions return HTML strings only - no Streamlit calls.
Caller must render with st.markdown(html, unsafe_allow_html=True).
"""


def stat_card(label, value, sub="", variant="default"):
    """
    Returns an HTML string for a metric card.
    
    Args:
        label: Metric label (displayed in uppercase)
        value: Main metric value (displayed in serif font)
        sub: Optional sub-label (displayed in muted text)
        variant: "default", "positive", "negative", or "gold"
    """
    border_colors = {
        "default": "var(--accent)",
        "positive": "var(--green)",
        "negative": "var(--red)",
        "gold": "var(--gold)"
    }
    
    border_color = border_colors.get(variant, border_colors["default"])
    sub_html = f'<div style="font-size: 11px; color: var(--ink-muted); margin-top: 4px;">{sub}</div>' if sub else ''
    
    return f"""
    <div style="
        background: var(--surface);
        border-left: 3px solid {border_color};
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 12px;
    ">
        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--ink-muted); margin-bottom: 8px;">
            {label}
        </div>
        <div style="font-family: var(--font-serif); font-size: 26px; color: var(--ink); letter-spacing: -0.5px;">
            {value}
        </div>
        {sub_html}
    </div>
    """


def section_card_open(title, icon="", subtitle=""):
    """
    Returns the opening HTML for a card section.
    Must be closed with section_card_close().
    
    Args:
        title: Section title
        icon: Optional emoji/icon prefix
        subtitle: Optional subtitle text
    """
    icon_html = f'<span style="margin-right: 8px;">{icon}</span>' if icon else ''
    subtitle_html = f'<div style="font-size: 13px; color: var(--ink-muted); margin-top: 4px;">{subtitle}</div>' if subtitle else ''
    
    return f"""
    <div class="card">
        <div style="margin-bottom: 20px;">
            <div style="font-family: var(--font-serif); font-size: 22px; color: var(--ink); margin-bottom: 4px;">
                {icon_html}{title}
            </div>
            {subtitle_html}
        </div>
        <div>
    """


def section_card_close():
    """Returns the closing HTML for a section card."""
    return """
        </div>
    </div>
    """


def signal_badge(signal):
    """
    Returns a pill badge HTML string for trading signals.
    
    Args:
        signal: "Buy", "Hold", or "Sell" (or "Sell / Avoid")
    """
    badge_classes = {
        "Buy": "badge-green",
        "Hold": "badge-amber",
        "Sell": "badge-red",
        "Sell / Avoid": "badge-red"
    }
    
    badge_class = badge_classes.get(signal, "badge-blue")
    
    return f'<span class="badge {badge_class}">{signal}</span>'


def ips_status_badge(status):
    """
    Returns a colored status indicator for IPS alignment.
    
    Args:
        status: "Aligned" or "Misaligned"
    """
    if status == "Aligned":
        return '<span class="badge badge-green">✓ Aligned</span>'
    else:
        return '<span class="badge badge-red">✗ Misaligned</span>'


def alert_box(message, variant="warn"):
    """
    Returns an alert box HTML string.
    
    Args:
        message: Alert message text
        variant: "warn" or "error"
    """
    if variant == "error":
        bg_color = "var(--red-light)"
        border_color = "var(--red)"
        icon = "⚠️"
        heading = "Error"
    else:
        bg_color = "var(--amber-light)"
        border_color = "var(--amber)"
        icon = "⚡"
        heading = "Warning"
    
    return f"""
    <div style="
        background: {bg_color};
        border-left: 4px solid {border_color};
        border-radius: 8px;
        padding: 16px 20px;
        margin: 16px 0;
    ">
        <div style="display: flex; align-items: flex-start; gap: 12px;">
            <span style="font-size: 20px;">{icon}</span>
            <div>
                <div style="font-weight: 600; color: var(--ink); margin-bottom: 4px;">
                    {heading}
                </div>
                <div style="font-size: 14px; color: var(--ink-soft); line-height: 1.5;">
                    {message}
                </div>
            </div>
        </div>
    </div>
    """


def hero_section(ips_profile_name=""):
    html = """<style>
.piq-hero * { box-sizing: border-box; }
.piq-hero {
    background: linear-gradient(150deg, #1a3d6e 0%, #0a1f3d 100%);
    border-radius: 20px;
    padding: 56px 52px 48px 52px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
    font-family: Arial, Helvetica, sans-serif;
}
.piq-hero-dots {
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background-image: radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px);
    background-size: 28px 28px;
    pointer-events: none;
}
.piq-hero-inner { position: relative; z-index: 2; }
.piq-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 30px;
    padding: 7px 18px;
    margin-bottom: 28px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #ffffff;
    font-family: Arial, sans-serif;
}
.piq-badge-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #4ade80;
    display: inline-block;
    flex-shrink: 0;
}
.piq-h1 {
    font-size: 52px;
    line-height: 1.08;
    letter-spacing: -1.5px;
    color: #ffffff;
    margin: 0 0 20px 0;
    font-weight: 700;
    font-family: Georgia, 'Times New Roman', serif;
}
.piq-h1-italic {
    font-style: italic;
    color: #7ab8f5;
    font-family: Georgia, 'Times New Roman', serif;
    font-weight: 400;
}
.piq-subtitle {
    font-size: 17px;
    font-weight: 300;
    line-height: 1.75;
    color: #a8c4e0;
    margin: 0 0 40px 0;
    max-width: 600px;
    font-family: Arial, sans-serif;
}
.piq-steps {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0;
    margin-bottom: 40px;
}
.piq-step {
    display: flex;
    align-items: center;
    gap: 14px;
    padding-right: 36px;
    margin-right: 36px;
    border-right: 1px solid rgba(255,255,255,0.15);
}
.piq-step:last-child {
    padding-right: 0;
    margin-right: 0;
    border-right: none;
}
.piq-step-num {
    width: 36px; height: 36px;
    border-radius: 50%;
    flex-shrink: 0;
    background: #2556a0;
    border: 2px solid rgba(255,255,255,0.35);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 800;
    color: #ffffff;
    font-family: Arial, sans-serif;
}
.piq-step-title {
    font-size: 15px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 3px;
    font-family: Arial, sans-serif;
}
.piq-step-sub {
    font-size: 12px;
    color: #7aa5cc;
    font-family: Arial, sans-serif;
}
.piq-trust {
    display: flex;
    flex-wrap: wrap;
    gap: 0;
    padding-top: 28px;
    border-top: 1px solid rgba(255,255,255,0.12);
    font-size: 15px;
    font-weight: 500;
    color: #7aa5cc;
    font-family: Arial, sans-serif;
}
.piq-trust span {
    padding: 0 16px;
    border-right: 1px solid rgba(255,255,255,0.2);
}
.piq-trust span:first-child {
    padding-left: 0;
}
.piq-trust span:last-child {
    border-right: none;
}
</style>

<div class="piq-hero">
  <div class="piq-hero-dots"></div>
  <div class="piq-hero-inner">

    <div class="piq-badge">
      <span class="piq-badge-dot"></span>
      Built for Financial Advisors
    </div>

    <div class="piq-h1">
      Institutional-Grade Portfolio Analysis,
      <br><span class="piq-h1-italic">in minutes.</span>
    </div>

    <div class="piq-subtitle">
      Generate a personalized IPS, analyze portfolio risk, run Monte Carlo
      stress tests, and export a client-ready PDF report &mdash; all in one workflow.
    </div>

    <div class="piq-steps">
      <div class="piq-step">
        <div class="piq-step-num">1</div>
        <div>
          <div class="piq-step-title">Define IPS</div>
          <div class="piq-step-sub">Goals &amp; risk profile</div>
        </div>
      </div>
      <div class="piq-step">
        <div class="piq-step-num">2</div>
        <div>
          <div class="piq-step-title">Analyze Portfolio</div>
          <div class="piq-step-sub">Risk, growth, signals</div>
        </div>
      </div>
      <div class="piq-step">
        <div class="piq-step-num">3</div>
        <div>
          <div class="piq-step-title">Stress Test</div>
          <div class="piq-step-sub">Monte Carlo + PDF</div>
        </div>
      </div>
    </div>

    <div class="piq-trust">
      <span>&#10003;&nbsp;IPS-aligned analysis</span>
      <span>&#10003;&nbsp;Real-time market data</span>
      <span>&#10003;&nbsp;Canadian &amp; US stocks</span>
      <span>&#10003;&nbsp;Professional PDF reports</span>
      <span>&#10003;&nbsp;Rules-based trade signals</span>
    </div>

  </div>
</div>
"""
    return html
