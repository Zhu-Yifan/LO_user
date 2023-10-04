# LO_user

## Introduction

The LO_user repository contains resources and (modified) codes related to [LiveOcean](https://faculty.washington.edu/pmacc/LO/LiveOcean.html) model fields analysis. It is greatly referred to and benefited from the [LO](https://github.com/parkermac/LO) github repository released by [Dr. Parker MacCready](https://faculty.washington.edu/pmacc/) at UW. 

## Feedbacks

(1) extract_moor.py


* Problem: during the exercise of extracting two desired mooring sites (DABOB) and (TWANOH) from the LO model fields. The script returned none data. 
* Cause: these two sites are close to shore, and not recognized as oceanic sites in model grid.
* Solve: run the related grid.nc, pcolor the "mask_rho", zoom into Hood Canal and pick (manually) the closest grid cell, write down the index, find the corresponding lon and lat, and re-run the extract_moor.py.