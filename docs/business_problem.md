# House Price Prediction: Business Problem Definition

**Status:** Draft v3. All thresholds are provisional and will be revised after the baselines are evaluated.
**Last updated:** 13 November 2026

---

## At a glance

| Question | Answer |
|----------|--------|
| **What is this?** | An ML tool that estimates the sale price of a house from details such as size, location, rooms and age. |
| **Who is it for?** | Buyers (am I overpaying?), sellers and agents (what price should I list at?). |
| **How is it delivered?** | Trained regression model → FastAPI service → simple web form. |
| **What it is not** | Not a real-estate marketplace and not a legal or appraisal-grade valuation. |
| **How do we judge it?** | Typical error of about 8% or less, extra attention to expensive homes, and it must clearly beat a simple "median price in that locality" guess. |

---

## 1. Problem statement

Given a few facts about a house that a user can easily provide, estimate its likely sale price, so that:

- **buyers** can sanity-check whether a price is fair, and
- **sellers and agents** can set a sensible listing price.

The estimate reflects the market period covered by the training data (see Section 9, Limitations).

## 2. Users and decisions

| Stakeholder | Decision the prediction supports |
|-------------|----------------------------------|
| Buyers | Check whether an asking price is fair, so they do not overpay. |
| Sellers | Decide what price to list the house at. |
| Real-estate agents | Advise buyers and sellers on pricing. |
| Platform / business team (indirect) | Offer estimates users can trust. |
| Data / ML team (us) | Build, evaluate and maintain the model. |

## 3. ML task and target

- **Task:** Supervised regression.
- **Target variable:** `SalePrice`, the final sale price of the house.
- **Why regression:** The target is a continuous number, not a category.

## 4. Inputs the user can realistically provide

The final feature list depends on the dataset chosen in Phase 2. The intended groups are:

| Group | Examples |
|-------|----------|
| Size | Living area, plot area, number of floors |
| Rooms | Bedrooms, bathrooms |
| Age and condition | Year built, renovation status, overall quality or condition |
| Location | Locality, city, or latitude/longitude (usually the strongest signal) |
| Property type | Apartment, villa, independent house |
| Amenities | Parking or garage, balcony, lift, furnishing |

**Excluded on principle**

| Feature | Reason |
|---------|--------|
| Price per sq ft | Derived from the target (data leakage). |
| Days on market | Only known after the listing exists; not available for a new property. |
| Seller's asking price | Circular, and it anchors the model to a human guess. |
| Anything recorded after the sale | Not available at prediction time. |

## 5. How success is measured

### 5.1 The main metric in plain words

**MdAPE (Median Absolute Percentage Error):** for each house, compute how far the prediction is from the true price as a percentage of the true price. Then take the middle value. An MdAPE of 8% means half of all predictions are within 8% of the real price.

### 5.2 Baselines

| ID | Baseline | Role |
|----|----------|------|
| B1 | Global mean price for every property | Sanity floor only. |
| B2 | Median sale price of the property's locality | **Primary competitor.** The model must beat this. |

### 5.3 Price segments

Segments are defined by percentiles of the test-set prices, so they adapt to whatever market the data covers.

| Segment | Definition |
|---------|-----------|
| Low | Bottom 25% of prices |
| Mid | 25th to 90th percentile |
| High ("expensive") | Top 10% of prices |

### 5.4 Model quality gates (all must pass to deploy)

| # | Check | Gate |
|---|-------|------|
| 1 | MdAPE, overall | ≤ 8% |
| 2 | Share of predictions within ±10% of actual, overall | ≥ 70% |
| 3 | MdAPE, Low segment | ≤ 10% |
| 4 | MdAPE, Mid segment | ≤ 8% |
| 5 | MdAPE, High segment | ≤ 12% |
| 6 | Improvement over B2 | MdAPE lower by at least 3 percentage points |
| 7 | Data leakage | No evidence of leakage in any feature |

If any gate fails, the model is not deployed.

### 5.5 Service requirement

| Check | Gate |
|-------|------|
| Prediction latency (P99, single request, measured locally in one container) | < 200 ms |

A load test at higher traffic is optional and is considered in Phase 14.

### 5.6 Diagnostic metrics (reported, not gates)

| Metric | Purpose |
|--------|---------|
| R² on log(target) | Share of variation explained (aim for ≥ 0.85) |
| RMSE on log(target) | Size of relative error. Log turns multiplicative (percentage) error into additive error. |
| MAE in currency units, per segment | Absolute error in business terms |
| Bias (mean signed error), per segment | Systematic over- or under-prediction |
| Top-15 feature importances | Stability check across cross-validation folds |

## 6. What "good enough" means in plain words

Buyers use the model to check for a fair price. Sellers and agents use it to price listings. Errors on expensive homes cost the most in absolute money, so that segment gets its own targets. A model with R² = 0.95 can still be unacceptable if it misses by more than 10% on expensive homes.

| Level for the High segment (top 10% of prices) | MdAPE |
|---|---|
| Minimum (deploy gate) | ≤ 12% |
| Target | ≤ 8% |
| Stretch | ≤ 5% (realistic only if data quality and feature coverage are strong) |

## 7. Cost of errors

| Error | Who is hurt |
|-------|-------------|
| Overprediction | Buyers overpay. |
| Underprediction | Sellers and agents lose money and margin. |

Both are treated as equally harmful, so we use symmetric metrics (MdAPE, RMSE on log target). An asymmetric loss function would be overkill here.

## 8. Out of scope

This project builds a price-estimation model and its service, not a real-estate platform. It will **not** include:

- appraisal-grade or legal valuation
- image features
- a live market-data feed
- automatic retraining
- user accounts

## 9. Constraints, assumptions and limitations

**Constraints (enforced by design)**

1. Every model feature must be available to the user at prediction time.
2. Preprocessing is fitted on training data only.
3. The test set is never used for tuning or feature decisions.

**Assumptions**

1. Sale prices in the data are genuine, not data-entry errors or non-market transfers.
2. Prices are in one currency and unit, and are not inflation-adjusted.
3. The market in the dataset resembles the market users will ask about (same city or region).
4. The same property does not appear in both train and test (duplicates or repeat sales).
5. User inputs fall inside the range the model saw in training. Outside it, the model is extrapolating.

**Limitations**

1. Estimates are not appraisals. The UI should say so and ideally show a range.
2. The data covers a specific period and region, so it may not represent the current market.
3. Location features can act as proxies for sensitive attributes. We note this and stay aware of it.
4. Post-deployment drift is not monitored in this project (discussed in Phase 14).

---

## Glossary

| Term | Meaning |
|------|---------|
| MdAPE | Median absolute percentage error (see 5.1). |
| Within ±10% | A prediction counts as a hit if it is within 10% of the true price. |
| Baseline | A simple benchmark the model must beat to prove it adds value. |
| Data leakage | Using information in training that would not exist at prediction time, which makes results look better than they really are. |
| Segment | A slice of the data by price range, used to check errors separately. |
| P99 latency | The response time that 99% of requests stay under. |
| Data drift | The market changing over time so that the model's patterns go stale. |
