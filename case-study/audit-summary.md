# Blue Mountains Data Handoff Audit

The ENGG2112 group project studied satellite fire detections in Blue Mountains
National Park during the 2019–20 fire season. My part of the project was to
verify the prepared data handoff and document the conditions under which the
labels could be interpreted.

## What I checked

| Check | Historical finding |
| --- | --- |
| Grid and date coverage | The prepared model panel contained 18,980 unique grid-day rows across 52 grid cells and 365 feature dates. |
| Feature and target alignment | Each target was aligned to the next UTC date in the same grid cell. The current-day detection feature was compared with the feature-day reference label. |
| Source data and label reconstruction | The audit reproduced the retained clean FIRMS table and daily labels, checked source hashes, and verified all 12 months of retained ERA5-Land coverage. |
| Modelling handoff | The park-overlap filter retained 15,695 rows across 43 grid cells. The active handoff specified 17 inputs for the full model and 16 for the conditions-only model. |

The audit passed 54 verifiable checks. Two questions remained open: whether each
grid and date had a usable satellite observation opportunity, and whether an
independent event record could confirm fire absence for zero-label rows.
The archive therefore supports a label for recorded detections and has limited
evidence about actual absence.

## Monthly coverage

[Monthly coverage CSV](monthly-coverage.csv) contains only the aggregate rows
from the historical audit. `calendar_days` counts dates present in the reference
label panel. It does not measure successful satellite observations.
`positive_cell_days` counts grid-day pairs with an eligible detection, which can
include multiple days from the same fire.

## Data and authorship

The group sourced active-fire detections from [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/content/active_fire/)
and hourly weather from [Copernicus ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land).
NSW National Parks and Wildlife Service boundary and fire history data supported
the study area and prescribed-burn checks. The original [source register](https://github.com/nedavaskachristopher-jpg/Group-3-2112/blob/d5014113ffb78eb80b6957a5a9f899d6077c4782/docs/evidence/source_access_and_licences.csv)
records the project data sources and attribution terms.

The forecasting model and full report were group deliverables. My contribution
here is the data-handoff audit, including the traceable checks and the
interpretation of zero labels. The group repository contains the [original audit notes](https://github.com/nedavaskachristopher-jpg/Group-3-2112/blob/d5014113ffb78eb80b6957a5a9f899d6077c4782/team/penelope_data_engineering/FINAL_DATA_AUDIT.md)
and [machine-readable evidence](https://github.com/nedavaskachristopher-jpg/Group-3-2112/blob/d5014113ffb78eb80b6957a5a9f899d6077c4782/docs/evidence/data_handoff_audit.json).
