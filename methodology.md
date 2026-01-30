# Methodology – Healthcare Accessibility Index

## 1. Study unit
The analysis is conducted at the **commune level** across Benin.  
All indicators are aggregated to the commune scale to enable territorial comparison.

---

## 2. Indicators

### 2.1 Spatial accessibility
Spatial accessibility is measured using the **average distance (in kilometers)** between localities and the nearest health facilities, aggregated by commune.

This indicator captures geographical constraints related to physical access to healthcare services.

---

### 2.2 Demographic pressure
Demographic pressure is calculated as:

Population / Number of health facilities

This indicator reflects the **potential demand per facility** and highlights service saturation, particularly in densely populated areas.

---

### 2.3 Facility capacity proxy
Health facility capacity is approximated using a **weighted classification** of facility types:

| Facility type        | Weight |
|----------------------|--------|
| National / Departmental hospitals | 1.0 |
| Zone hospitals       | 1.0 |
| Health centers / Clinics | 0.6 |
| Maternities          | 0.5 |
| Dispensaries         | 0.4 |
| Village health units | 0.2 |

The average weight per commune is used as a proxy for healthcare service capacity.

---

## 3. Normalization
All indicators are normalized using **min–max scaling** to ensure comparability:

(X − min) / (max − min)

This step prevents any single indicator from dominating the composite index due to scale differences.

---

## 4. Composite accessibility index
The baseline healthcare accessibility index (Scenario A) is computed as:

(Distance_norm + Pressure_norm) / Capacity_weight

Higher index values indicate **worse healthcare accessibility**, while lower values indicate better access.

---

## 5. Classification
The composite index is classified into **four accessibility levels** using a **quantile-based approach**:

- Good access  
- Medium access  
- Poor access  
- Very Poor access  

This method ensures balanced class distribution for comparative analysis.

---

## 6. Sensitivity analysis
A sensitivity analysis is conducted by modifying the relative importance of indicators:

- Scenario A: Balanced (baseline)
- Scenario B: Distance prioritized
- Scenario C: Demographic pressure prioritized
- Scenario D: Stronger influence of facility capacity

Changes in accessibility classes across scenarios are used to assess index robustness.

---

## 7. Urban–rural comparison
Urban communes are defined as:
- Cotonou
- Abomey-Calavi
- Porto-Novo
- Parakou

Accessibility patterns are compared between urban and rural communes using:
- descriptive statistics
- cross-tabulation of accessibility classes

---

## 8. Limitations
This analysis is exploratory and subject to several limitations:
- Facility capacity is approximated using facility type rather than service volume
- Travel time and transport infrastructure are not explicitly modeled
- Results depend on data quality and classification thresholds

---

## 9. Intended use
The index is designed for **comparative spatial analysis and decision support**, not for direct operational planning at facility level.
