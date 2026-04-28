from langchain_core.tools import tool

@tool
def calculate_dcf_value(free_cash_flow: float, growth_rate: float=0.05, discount_rate: float = 0.105, terminal_growth: float=0.025, years:int= 5) -> dict:
    """
    Calculate Discounted Cash Flow (DCF) valuation.

    Args:
        free_cash_flow: Base year FCF in millions
        growth_rate: Annual growth rate for projection period (default 5%)
        discount_rate: WACC for discounting (default 10.5%)
        terminal_growth: Perpetual growth rate (default 2.5%)
        years: Number of projection years (default 5)

    Returns:
        Dictionary with projected cash flows and enterprise value
    """
    projected_fcf = []
    current_fcf = free_cash_flow

    for year in range(1, years+1):
        current_fcf *= (1+growth_rate)
        discounted = current_fcf/((1+discount_rate)**year)
        projected_fcf.append({
            "year": year,
            "undiscounted": round(current_fcf, 2),
            "discounted": round(discounted, 2)
        })
        terminal_value = (current_fcf * (1+terminal_growth))/(discount_rate-terminal_growth)
        terminal_discounted = terminal_value / ((1+discount_rate)**years)
        total_ev = sum(p["discounted"] for p in projected_fcf) + terminal_discounted
        return {
            "projected_cash_flows": projected_fcf, 
            "terminal_value": round(terminal_value, 2),
            "terminal_discounted": round(terminal_discounted, 2),
            "enterprise_value": round(total_ev, 2)
        }
@tool
def assess_risk_profile(age: int, investment_horizon: int, risk_tolerance: str="moderate") -> dict:
    """
    Assess user's risk profile based on age and horizon.
    Args:
        age: User's current age
        investment_horizon: Years until retirement/goal
        risk_tolerance: User's stated tolerance (conservative/moderate/aggressive)
    
    Returns:
        Recommended asset allocation and risk score
    """
    # Rule based risk assessment
    if risk_tolerance == "conservative" or investment_horizon < 5:
        allocation = {"equity": 0.2, "debt": 0.6, "gold": 0.2}
        risk_score = 2
    elif risk_tolerance == "aggressive" and investment_horizon > 10:
        allocation = {"equity": 0.7, "debt": 0.2, "gold": 0.1}
        risk_score = 8
    else:
        allocation = {"equity": 0.5, "debt": 0.4, "gold": 0.1}
        risk_score = 5
    return {
        "risk_score": risk_score,
        "recommended_allocation": allocation,
        "rationale": "Based on age {age} and {investment_horizon}-year horizon "
    }
@tool
def calculate_retirement_corpus(
    monthly_expenses: float,
    current_age: int,
    retirement_age: int = 60,
    life_expectancy: int = 85,
    inflation_rate: float = 0.06,
    # pre_ret_return: float = 0.12,
    post_ret_return: float = 0.08
) -> dict:
    """
    Calculate required retirement corpus using SWP method.
    Args:
        monthly_expenses: Current monthly expenses in rupees
        current_age: Current age in years
        retirement_age: Planned retirement age (default 60)
        life_expectancy: Expected lifespan (default 85)
        inflation_rate: Annual inflation rate (default 6%)
        pre_ret_return: Expected returns before retirement (default 12%)
        post_ret_return: Expected returns after retirement (default 8%)
    
    Returns:
        Required corpus and monthly withdrawal at retirement
    """ 
    years_to_retirement = retirement_age-current_age
    retirement_years = life_expectancy - retirement_age
    inflated_expense = monthly_expenses * ((1+inflation_rate) ** years_to_retirement)
    monthly_rate = (1+post_ret_return) ** (1/12)-1
    months = retirement_years * 12
    corpus = inflated_expense * (1-(1+monthly_rate)** -months)/monthly_rate
    return {
        "monthly_expense_current": monthly_expenses,
        "monthly_expense_at_retirement": round(inflated_expense, 2),
        "required_corpus": round(corpus, 2),
        "years_to_retirement": years_to_retirement,
        "retirement_years": retirement_years 
    }

    

