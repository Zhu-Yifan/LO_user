## README for stressor

#### This folder contains codes to extract marine extreme events including Marine Heat Waves, Hypoxia, and Ocean Acidification.  

---

### MHWs
Marine heatwaves (MHWs) are extreme warming events that are becoming more severe, frequent, and prolonged due to climate change. MHWs are defined as extended, distinct periods of unusually high seawater temperatures (Hobday et al., 2016). Specifically, an MHW occurs when seawater temperatures at a specific location exceed the local 90th percentile based on a 30-year fixed climatology (Fig. 1).
One of the most recent and severe MHWs in the northeast Pacific was the **"Blob"** of 2014–2016, which led to numerous ecological disturbances, including harmful algal blooms, mass seabird mortality, and shifts in community structures within kelp forests of the California Current System.

<p align="center">
  <img src="https://github.com/Zhu-Yifan/LO_user/blob/master/extract/stressor/Figure/mhws.png" alt="Figure 1. MHWs definition" width="650" height="400">
</p>

### Table of content
| Module |      Anlysis      |    Comments                                |                                                                          
|:-----------------:|:-----------------------------------------------:|:----------------------------------------------------------------------------------------------------------------:|
|[ OISST climatology and anomaly](https://github.com/Zhu-Yifan/LO_user/blob/master/extract/stressor/MHW/mhw_utilities.py)| [Plot OISST MHWs](https://github.com/Zhu-Yifan/LO_user/blob/master/extract/stressor/MHW/heatwave_times_series.py)               |  ...    |  
|[Extract MHWs metric](https://github.com/Zhu-Yifan/LO_user/blob/master/extract/stressor/MHW/marineHeatWaves.py)|           [Visulize WHW metrics](https://github.com/Zhu-Yifan/LO_user/blob/master/extract/stressor/MHW/mhw_stats.ipynb)                         | ... |             
| [Ocetrac](https://ocetrac.readthedocs.io/en/latest/index.html) |  ... | ...|                       



### Hypoxia
Hypoxia refers to a condition where Hypoxia in marine systems refers to a condition where the dissolved oxygen (DO) concentration in the water falls to levels that are insufficient to sustain most aerobic organisms. While the specific threshold can vary, hypoxia is typically defined as a DO concentration below 2 mg/L (= 1.4 ml/L, Fig. 2) or ~30% saturation.
Hypoxia causes physiological stress, reduced growth rates, impaired reproduction, and, at extreme levels, mass mortality (e.g., die off events of fish, crabs, lobster). Sediment-dwelling organisms are particularly vulnerable because they cannot escape hypoxic conditions. Prolonged hypoxia can lead to benthic dead zones.

<p align="center">
  <img src="https://github.com/Zhu-Yifan/LO_user/blob/master/extract/stressor/Figure/hypoxia_thereshold.jpg" alt="Figure 2. hypoxia threshold" width="700" height="400">
</p>

Hypoxia occurs in both natural and anthropogenic contexts, mostly in continental shelves (<200 m), coastal seas (e.g., Baltic Sea), estuaries (e.g., Chesapeake Bay). In these systems, hypoxia is strongly seasonal. Additionally, there are Oxygen Minimum Zones (OMZs) at mid-depths (200–1000 m) in the open ocean (e.g., Eastern Tropical North and South Pacific, Arabian Sea), driven by sluggish circulation and high organic matter decomposition.
Expanding hypoxia areas due to climate change threaten marine ecosystems, and will limit suitable habitat for marine life.

<p align="center">
  <img src="https://github.com/Zhu-Yifan/LO_user/blob/master/extract/stressor/Figure/hypoxic_areas.jpeg" alt="Figure 3. hypoxia map">
</p>

### Table of content
| Module | Anlysis |    Comments                                |                                                                          
|:------:|:-------:|:----------------------------------------------------------------------------------------------------------------:|
|  ...   |   ...   |  ...    |  
|  ...   |   ...   | ... |             
|  ...   |   ...   | ...|                       


### Ocean Acidification 
Ocean acidification (OA) refers to the ongoing change in seawater chemistry across Earth's oceans, primarily driven by the absorption of about a quarter of anthropogenic carbon dioxide (CO2) emissions. This process decreases ocean pH levels and carbonate ion concentrations, impacting the formation of calcium carbonate-based structures of marine organisms such as corals, shellfish, and certain planktonic species, which might have cascading effects on marine food webs and ecosystem functioning.
<p align="center">
  <img src="https://github.com/Zhu-Yifan/LO_user/blob/master/extract/stressor/Figure/pmel-oa-imageee.jpg" alt="Figure 4. OA" width="600" height="400">
>
</p>

The indicators of OA include pCO2, pH, aragonite saturation state, calcite saturation state, total dissolved inorganic carbon content, and total alkalinity content.

### Table of content
| Module | Anlysis |    Comments                                |                                                                          
|:------:|:-------:|:----------------------------------------------------------------------------------------------------------------:|
|  ...   |   ...   |  ...    |  
|  ...   |   ...   | ... |             
|  ...   |   ...   | ...|                       
---

### References
##### MHWs
- Alistair J. Hobday et al. (2016). A hierarchical approach to defining marine heatwaves. Progress in Oceanography. https://doi.org/10.1016/j.pocean.2015.12.014.
- Oliver et al. (2021). Marine heatwaves. Annual review of marine science. https://doi.org/10.1146/annurev-marine-032720-095144
- Smith et al. (2023). Biological impacts of marine heatwaves. Annual Review of Marine Science. https://www.annualreviews.org/content/journals/10.1146/annurev-marine-032122-121437
- McCabe et al. (2016). An unprecedented coastwide toxic algal bloom linked to anomalous ocean conditions. Geophysical Research Letters. https://onlinelibrary.wiley.com/doi/abs/10.1002/2016GL070023
- Piatt et al. (2020). Extreme mortality and reproductive failure of common murres resulting from the northeast Pacific marine heatwave of 2014-2016. PLoS ONE. https://doi.org/10.1371/journal.pone.0226087
- Michaud, K.M., Reed, D.C. & Miller, R.J. (2022) The Blob marine heatwave transforms California kelp forest ecosystems. https://doi.org/10.1038/s42003-022-04107-z
- Scannell et al. (2020). Subsurface evolution and persistence of marine heatwaves in the Northeast Pacific. Geophysical Research Letters. https://doi.org/10.1029/2020GL090548

##### Hypoxia
- Chan, F., J.A. Barth, K.J. Kroeker, J. Lubchenco, and B.A. Menge. 2019. The dynamics and impact of ocean acidification and hypoxia: Insights from sustained investigations in the Northern California Current Large Marine Ecosystem. Oceanography 32(3):62–71, https://doi.org/10.5670/oceanog.2019.312.
- Breitburg, D., Levin, L. A., Oschlies, A., Grégoire, M., Chavez, F. P., Conley, D. J., ... & Zhang, J. (2018). Declining oxygen in the global ocean and coastal waters. Science, 359(6371), eaam7240. https://doi.org/10.1371/10.1126/science.aam7240
- Deutsch, C., Ferrel, A., Seibel, B., Pörtner, H. O., & Huey, R. B. (2015). Climate change tightens a metabolic constraint on marine habitats. Science, 348(6239), 1132-1135. https://doi.org/10.1126/science.aaa1605

##### OA
- Feely, R. A., Carter, B. R., Alin, S. R., Greeley, D., & Bednaršek, N. (2024). The combined effects of ocean acidification and respiration on habitat suitability for marine calcifiers along the west coast of North America. Journal of Geophysical Research: Oceans, 129, e2023JC019892. https://doi.org/10.1029/2023JC019892
- Jiang, L.-Q., Dunne, J., Carter, B. R., Tjiputra, J. F., Terhaar, J., Sharp, J. D., et al. (2023). Global surface ocean acidification indicators from 1750 to 2100. Journal of Advances in Modeling Earth Systems, 15, e2022MS003563. https://doi.org/10.1029/2022MS003563
- Bednaršek, Nina, Richard A. Feely, Greg Pelletier, and Flora Desmet. “GLOBAL SYNTHESIS OF THE STATUS AND TRENDS OF OCEAN ACIDIFICATION IMPACTS ON SHELLED PTEROPODS.” Oceanography 36, no. 2/3 (2023): 130–37. https://www.jstor.org/stable/27257891.