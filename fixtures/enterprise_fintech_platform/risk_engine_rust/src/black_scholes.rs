use std::f64::consts::PI;

/// Normal Cumulative Distribution Function approximation
pub fn cdf_normal(x: f64) -> f64 {
    let a1 = 0.254829592;
    let a2 = -0.284496736;
    let a3 = 1.421413741;
    let a4 = -1.453152027;
    let a5 = 1.061405429;
    let p = 0.3275911;

    let sign = if x < 0.0 { -1.0 } else { 1.0 };
    let abs_x = x.abs() / std::f64::consts::SQRT_2;

    let t = 1.0 / (1.0 + p * abs_x);
    let erf = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * (-abs_x * abs_x).exp();

    0.5 * (1.0 + sign * erf)
}

/// Normal Probability Density Function
pub fn pdf_normal(x: f64) -> f64 {
    (1.0 / (2.0 * PI).sqrt()) * (-0.5 * x * x).exp()
}

pub struct OptionParameters {
    pub spot_price: f64,
    pub strike_price: f64,
    pub time_to_maturity_years: f64,
    pub risk_free_rate: f64,
    pub volatility: f64,
}

pub struct Greeks {
    pub call_price: f64,
    pub put_price: f64,
    pub delta_call: f64,
    pub delta_put: f64,
    pub gamma: f64,
    pub vega: f64,
    pub theta_call: f64,
}

pub fn calculate_greeks(params: &OptionParameters) -> Greeks {
    let s = params.spot_price;
    let k = params.strike_price;
    let t = params.time_to_maturity_years;
    let r = params.risk_free_rate;
    let v = params.volatility;

    let sqrt_t = t.sqrt();
    let d1 = ((s / k).ln() + (r + 0.5 * v * v) * t) / (v * sqrt_t);
    let d2 = d1 - v * sqrt_t;

    let nd1 = cdf_normal(d1);
    let nd2 = cdf_normal(d2);
    let n_neg_d1 = cdf_normal(-d1);
    let n_neg_d2 = cdf_normal(-d2);
    let npd1 = pdf_normal(d1);

    let discount = (-r * t).exp();

    let call_price = s * nd1 - k * discount * nd2;
    let put_price = k * discount * n_neg_d2 - s * n_neg_d1;

    let delta_call = nd1;
    let delta_put = nd1 - 1.0;
    let gamma = npd1 / (s * v * sqrt_t);
    let vega = s * sqrt_t * npd1 * 0.01;
    let theta_call = (- (s * npd1 * v) / (2.0 * sqrt_t) - r * k * discount * nd2) / 365.0;

    Greeks {
        call_price,
        put_price,
        delta_call,
        delta_put,
        gamma,
        vega,
        theta_call,
    }
}
