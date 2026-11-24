# Dataset Notes: Ames Housing

These notes describe the data used in the House Price Prediction project: where it came from, what it contains, and what problems we already know about. They will be updated as we learn more.

---

## 1. Source and citation

**Original source:** Ames City Assessor's Office, Ames, Iowa. The data was put together and documented by Dean De Cock.

**Citation:** De Cock, D. (2011). "Ames, Iowa: Alternative to the Boston Housing Data as an End of Semester Regression Project." *Journal of Statistics Education*, 19(3). https://doi.org/10.1080/10691898.2011.11889627

**Column descriptions (documentation):** https://jse.amstat.org/v19n3/decock/DataDocumentation.txt

**Copy used in this project:** Kaggle, "Ames Housing Dataset", uploaded by Marco Palermo. https://www.kaggle.com/datasets/marcopale/housing

**File:** `AmesHousing.csv`, downloaded on 23 November 2026.

**Checked shape:** 2,930 rows x 82 columns.

**License:** GPL 2 (as shown on the Kaggle page).

---

## 2. What one row means

One row is the sale of one house in Ames, Iowa. No parcel ID (`PID`) appears twice, so no house is repeated in the data. This supports our Assumption 4 (the same property is not in both train and test).

## 3. Target, unit and time period

- **Target column:** `SalePrice`
- **Unit:** US dollars (not adjusted for inflation)
- **Time period:** Houses sold between 2006 and 2010. The columns `Mo Sold` and `Yr Sold` give the month and year of each sale.
- **Place:** One small US city (Ames, Iowa). Prices here may not match other cities or today's market.

## 4. Size of the data

- **Shape:** 2,930 rows, 82 columns
- **Column types:** 43 text, 28 whole-number, 11 decimal
- **Duplicate rows:** 0
- **Repeated `PID`:** 0

**Price summary (from our first look):**

| Statistic | Value (USD) |
|-----------|-------------|
| Minimum | 12,789 |
| 25th percentile | 129,500 |
| Median | 160,000 |
| Mean | 180,796 |
| 75th percentile | 213,500 |
| Maximum | 755,000 |

The mean is higher than the median, so a few very expensive houses pull the average up. This is called right skew. It is the reason we also look at the log of the price.

---

## 5. Columns grouped by our Section 4 feature groups

This is a first draft. Not every column below will end up in the final model. We will decide in the EDA and preprocessing phases.

**Size**
`Lot Area`, `Lot Frontage`, `Gr Liv Area`, `1st Flr SF`, `2nd Flr SF`, `Low Qual Fin SF`, `Total Bsmt SF`, `BsmtFin SF 1`, `BsmtFin SF 2`, `Bsmt Unf SF`, `Mas Vnr Area`, `Garage Area`, `Wood Deck SF`, `Open Porch SF`, `Enclosed Porch`, `3Ssn Porch`, `Screen Porch`, `Pool Area`

**Rooms**
`Bedroom AbvGr`, `Kitchen AbvGr`, `TotRms AbvGrd`, `Full Bath`, `Half Bath`, `Bsmt Full Bath`, `Bsmt Half Bath`

**Age and condition**
`Year Built`, `Year Remod/Add`, `Garage Yr Blt`, `Overall Qual`, `Overall Cond`, `Exter Qual`, `Exter Cond`, `Bsmt Qual`, `Bsmt Cond`, `Heating QC`, `Kitchen Qual`, `Fireplace Qu`, `Garage Qual`, `Garage Cond`, `Pool QC`, `Functional`

**Location**
`Neighborhood`, `MS Zoning`, `Condition 1`, `Condition 2`, `Street`, `Alley`, `Lot Shape`, `Land Contour`, `Land Slope`, `Lot Config`

**Property type**
`MS SubClass`, `Bldg Type`, `House Style`, `Foundation`, `Roof Style`, `Roof Matl`, `Exterior 1st`, `Exterior 2nd`, `Mas Vnr Type`

**Amenities and utilities**
`Garage Type`, `Garage Finish`, `Garage Cars`, `Fireplaces`, `Central Air`, `Heating`, `Electrical`, `Utilities`, `Paved Drive`, `Fence`, `Bsmt Exposure`, `BsmtFin Type 1`, `BsmtFin Type 2`, `Misc Feature`, `Misc Val`

**Not yet placed (see open decisions)**
`Mo Sold`, `Yr Sold`

---

## 6. Columns we will NOT use as features

| Column | Reason |
|--------|--------|
| `Order`, `PID` | They only identify a row. They carry no pricing information and can create fake patterns. |
| `Sale Type` | It describes how the sale was made (the legal or financial arrangement). We do not know this before the house is sold, so using it would break our rule that every feature must be available at prediction time. |
| `Sale Condition` | It describes special circumstances of the sale, such as non-market sales. We do not know it before the sale either. |
| `SalePrice` | This is the target, not a feature. |

**Note:** `Sale Condition` is not usable as a feature, but it may still be useful for cleaning the data. Our Assumption 1 says prices come from real market sales. If we find abnormal or non-market sales, we may remove those rows from the training data. We will decide this in EDA.

---

## 7. Known data issues

1. **Many "missing" values are not really missing.** In columns such as `Pool QC`, `Misc Feature`, `Alley`, `Fence` and `Fireplace Qu`, the documentation says "NA" means the house does not have that feature. The same idea applies to the garage and basement columns. Pandas reads the text "NA" and "None" as missing values by default. For example, `Mas Vnr Type` shows 1,775 missing values, and most of them are probably the word "None" (no masonry veneer). If we drop or fill these blindly, we lose real information.

2. **`Lot Frontage` has 490 missing values.** This one looks like truly missing data, because every house has some lot frontage. It needs a proper filling method (imputation).

3. **`Garage Yr Blt` has 159 missing values.** This probably means the house has no garage. Needs checking in EDA.

4. **`MS SubClass` is stored as numbers but is really a category code.** The numbers are labels, not amounts, so they must not be treated like a normal number column.

5. **Price is right-skewed.** The mean is above the median, and the maximum is far above the 75th percentile. We will check outliers and use log(price) where it helps.

6. **Very large houses may need checking.** I believe the documentation suggests looking at houses with more than about 4,000 sq ft of living area. This must be confirmed in `DataDocumentation.txt` and checked in EDA.

7. **Some size columns may overlap.** `Gr Liv Area` may be close to `1st Flr SF` + `2nd Flr SF` + `Low Qual Fin SF`. If true, these columns carry the same information twice. To verify in EDA.

**Check to run (fill in the result after running):**

```python
raw = pd.read_csv("data/AmesHousing.csv", keep_default_na=False)
print(raw["Alley"].value_counts())
print(raw["Mas Vnr Type"].value_counts())
```

Result: _( In `Alley`, 2,732 rows have the text "NA" (no alley access). In `Mas Vnr Type`, 1,752 rows have the text "None" (no veneer) and only 23 rows are truly blank. So pandas showed 1,775 missing values, but only 23 are really missing.)_

---

## 8. Open decisions (to settle in Phase 4 EDA and Phase 5 preprocessing)

1. **Do we use `Yr Sold` and `Mo Sold`?** A user asking today is outside 2006 to 2010, and the model cannot predict for a year it never saw. They may be used only for analysis, not as inputs.
2. **Which inputs will the user really type in?** Section 4 of our business document says inputs must be ones the user can realistically provide. A buyer may not know `Bsmt Exposure`, `Exter Cond` or `Roof Matl`. A web form cannot ask for about 70 fields. We will likely choose a small set of user inputs (about 10 to 15) and treat the rest as extra columns for analysis.
3. **Do we remove abnormal or non-market sales from training?** Use `Sale Condition` as a row filter, not as a feature (see Section 6).
4. **How do we handle outliers** (very large or very expensive houses)?
5. **How do we handle the "NA means absent" columns** (see issue 1)?
