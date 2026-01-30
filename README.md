# Healthcare Accessibility in Benin 🇧🇯

**Commune-level spatial analysis of healthcare accessibility using GIS and Python**

This project analyzes healthcare accessibility across the 77 communes of Benin using a **composite spatial index** that integrates distance to health facilities, demographic pressure, and facility capacity.  
It also explores **urban–rural disparities** and tests the **robustness of results through sensitivity analysis**.

---

## 🎯 Objectives
- Measure healthcare accessibility at the **commune level**
- Identify spatial inequalities across Benin
- Test whether **urban status guarantees better access**
- Assess the **sensitivity** of results to modeling assumptions

---

## 🧠 Key Findings
- **Urban status does not guarantee good healthcare access**
- Major urban communes (**Cotonou, Abomey-Calavi, Porto-Novo, Parakou**) are classified between **medium and very poor access**
- Some rural communes show moderate accessibility due to lower demographic pressure
- Accessibility patterns remain generally stable, but **specific communes are sensitive to weighting choices**

---

## 🗺️ Method Overview
- Construction of a **composite accessibility index** combining:
  - Average distance to health facilities
  - Population pressure
  - Facility capacity (weighted by facility type)
- Indicators normalized using **min–max scaling**
- Aggregation at the **commune level**
- Classification into four accessibility levels using a **quantile-based approach**
- Sensitivity analysis performed by testing multiple weighting scenarios
- Urban–rural comparison based on administrative status

📄 Full methodology available in [`methodology.md`](methodology.md)

---

## 📊 Outputs
- Commune-level **Healthcare Accessibility Map**
- **Sensitivity Analysis Map**
- Urban vs Rural accessibility comparison tables

All outputs are available in the `outputs/` directory.

---


## Maps (PDF)
- Health Accessibility Index map: `outputs/maps/health_access_map.pdf`
- Sensitivity analysis map: `outputs/maps/sensitivity_map.pdf`
- Urban–Rural comparison map: `outputs/maps/urban_rural_map.pdf`

## Quick preview
![Health access map](outputs/maps/health_access_map.jpeg)
![Sensitivity map](outputs/maps/sensitivity_map.jpeg)
![Urban–Rural map](outputs/maps/urban_rural_map.jpeg)


## 🛠️ Tools & Technologies
- **Python** (pandas, geopandas)
- **QGIS** (cartography & spatial styling)
- **Spatial analysis & GIS modeling**
- Reproducible project structure (GitHub-ready)


---

## 📌 Data Sources
- Health facilities: **Ministry of Health, Benin**
- Population data: **RGPH4 – INStaD**
- Administrative boundaries: **IGN Benin**

---

## 👤 Author
**N’tcha Joas N’dah**  
MSc Geomatics Engineering  
GIS & Python – Spatial Analysis  
2026


---

## 📁 Project Structure
