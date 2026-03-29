# IPS Engine - CFA-Compliant Investment Policy Statement Generator

def calculate_ips(time_horizon, liquidity, objective, crash_reaction, knowledge):
    """
    Calculate risk profile based on Ability vs Willingness to take risk
    Returns: (risk_profile, targets_dict)
    """
    print(f"🎯 IPS Inputs: Time={time_horizon}, Liquidity={liquidity}, Objective={objective}, Crash={crash_reaction}, Knowledge={knowledge}")
    
    # Calculate Ability to take risk (objective factors)
    ability_score = 0
    
    # Time horizon scoring (1-30 years)
    if time_horizon <= 3:
        ability_score += 0  # Very low ability
    elif time_horizon <= 7:
        ability_score += 2  # Moderate ability  
    else:
        ability_score += 4  # High ability
    
    # Liquidity needs scoring
    if liquidity == 'None (0%)':
        ability_score += 2  # High ability
    elif liquidity == 'Low (< 10%)':
        ability_score += 1  # Moderate ability
    elif liquidity == 'Moderate (10-25%)':
        ability_score += 0  # Low ability
    else:  # High (> 25%)
        ability_score -= 1  # Very low ability (negative score)
    
    # Calculate Willingness to take risk (behavioral factors)
    willingness_score = 0
    
    # Objective scoring
    if objective == 'Capital Preservation':
        willingness_score += 0
    elif objective == 'Steady Income':
        willingness_score += 1
    elif objective == 'Balanced Growth':
        willingness_score += 2
    else:  # Maximum Capital Appreciation
        willingness_score += 3
    
    # Crash reaction scoring
    if crash_reaction == 'Sell to avoid further losses':
        willingness_score -= 2  # Very low willingness
    elif crash_reaction == 'Do nothing and wait':
        willingness_score += 1  # Moderate willingness
    else:  # Buy more at a discount
        willingness_score += 3  # High willingness
    
    # Knowledge scoring
    if knowledge == 'Novice':
        willingness_score += 0
    elif knowledge == 'Intermediate':
        willingness_score += 1
    elif knowledge == 'Advanced':
        willingness_score += 2
    else:  # Expert
        willingness_score += 3
    
    print(f"📊 Ability Score: {ability_score}, Willingness Score: {willingness_score}")
    
    # Determine risk profile
    # Conservative: Low ability OR low willingness overrides high willingness
    # Aggressive: High ability AND high willingness
    # Moderate: Everything else
    
    if ability_score <= 1 or willingness_score <= 0:
        risk_profile = 'Conservative'
    elif ability_score >= 5 and willingness_score >= 5:
        risk_profile = 'Aggressive'
    else:
        risk_profile = 'Moderate'
    
    print(f"🎯 Final Risk Profile: {risk_profile}")
    
    return risk_profile, get_ips_targets(risk_profile)

def get_ips_targets(risk_profile):
    """Return CFA-compliant strict target ranges for each risk profile"""
    targets = {
        'Conservative': {
            'beta_range': (0.0, 0.85),
            'volatility_range': (0.0, 0.08),  # < 8%
            'yield_min': 0.04,  # > 4%
            'yield_max': 1.0,  # No upper limit
            'description': 'Capital Preservation with Income Focus'
        },
        'Moderate': {
            'beta_range': (0.85, 1.05),
            'volatility_range': (0.08, 0.15),  # 8-15%
            'yield_min': 0.02,  # > 2%
            'yield_max': 0.04,  # < 4%
            'description': 'Balanced Growth with Moderate Risk'
        },
        'Aggressive': {
            'beta_range': (1.05, 1.30),
            'volatility_range': (0.15, 0.25),  # 15-25%
            'yield_min': 0.0,  # No minimum
            'yield_max': 0.02,  # < 2%
            'description': 'Maximum Capital Appreciation with Higher Risk'
        }
    }
    
    return targets.get(risk_profile, targets['Moderate'])

def assess_alignment(actual_metrics, ips_targets, profile):
    """
    Compare portfolio metrics against IPS targets and provide actionable feedback
    Returns: {'is_aligned': bool, 'bullets': list}
    """
    alignment_bullets = []
    
    # Extract actual metrics
    actual_beta = actual_metrics.get('portfolio_beta', 0)
    actual_volatility = actual_metrics.get('annual_volatility', 0)
    actual_yield = actual_metrics.get('weighted_dividend_yield', 0) / 100  # Convert from percentage to decimal
    
    # Extract target ranges
    beta_min, beta_max = ips_targets['beta_range']
    vol_min, vol_max = ips_targets['volatility_range']
    yield_min = ips_targets.get('yield_min', 0)
    yield_max = ips_targets.get('yield_max', 1.0)
    
    # Assess Beta alignment
    if beta_min <= actual_beta <= beta_max:
        alignment_bullets.append(f"✅ **Portfolio Beta ({actual_beta:.2f})** is within your target range of {beta_min:.2f} - {beta_max:.2f}")
    else:
        if actual_beta > beta_max:
            alignment_bullets.append(f"⚠️ **Portfolio Beta ({actual_beta:.2f})** exceeds your maximum target of {beta_max:.2f}. Consider reducing exposure to high-volatility growth stocks or adding defensive positions to align with your {profile} profile.")
        else:
            alignment_bullets.append(f"⚠️ **Portfolio Beta ({actual_beta:.2f})** is below your minimum target of {beta_min:.2f}. Consider adding growth-oriented stocks to increase market sensitivity for your {profile} objectives.")
    
    # Assess Volatility alignment
    if vol_min <= actual_volatility <= vol_max:
        alignment_bullets.append(f"✅ **Annualized Volatility ({actual_volatility:.1%})** is within your target range of {vol_min:.1%} - {vol_max:.1%}")
    else:
        if actual_volatility > vol_max:
            alignment_bullets.append(f"⚠️ **Annualized Volatility ({actual_volatility:.1%})** exceeds your maximum target of {vol_max:.1%}. Consider diversifying across sectors, adding lower-volatility assets, or reducing concentration in high-beta stocks to match your {profile} risk tolerance.")
        else:
            alignment_bullets.append(f"⚠️ **Annualized Volatility ({actual_volatility:.1%})** is below your minimum target of {vol_min:.1%}. Your portfolio may be too conservative for your {profile} growth objectives. Consider adding growth stocks or reducing bond exposure.")
    
    # Assess Yield alignment
    if yield_min <= actual_yield <= yield_max:
        alignment_bullets.append(f"✅ **Dividend Yield ({actual_yield:.2%})** is within your target range of {yield_min:.1%} - {yield_max:.1%}")
    else:
        if actual_yield < yield_min:
            alignment_bullets.append(f"⚠️ **Dividend Yield ({actual_yield:.2%})** is below your minimum target of {yield_min:.1%}. Consider adding dividend-paying stocks or income-focused assets to meet your {profile} income requirements.")
        else:
            alignment_bullets.append(f"⚠️ **Dividend Yield ({actual_yield:.2%})** exceeds your maximum target of {yield_max:.1%}. Consider reducing income-focused holdings to better align with your {profile} growth objectives.")
    
    # Overall alignment assessment
    aligned_count = sum(1 for bullet in alignment_bullets if bullet.startswith("✅"))
    total_checks = len(alignment_bullets)
    is_aligned = aligned_count == total_checks
    
    if is_aligned:
        alignment_bullets.insert(0, f"🎉 **Perfect Alignment!** Your portfolio is fully compliant with your {profile} Investment Policy Statement across all key risk metrics.")
    else:
        alignment_bullets.insert(0, f"📊 **Alignment Status: {aligned_count}/{total_checks} metrics within target ranges.** Your portfolio needs adjustments to fully align with your {profile} risk profile.")
    
    return {
        'is_aligned': is_aligned,
        'bullets': alignment_bullets
    }
