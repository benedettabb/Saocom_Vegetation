Processing of SAOCOM data to obtain vegetation information.

SNAP gpt pre-processing:
  Cal --> TF --> TC --> dB
Exported bands: VH, VV, Local Projected Incidence Angle

GDAL Processing:
  Rename files (to add acquisition DateTime, Subswath, Orbit)
  Setting of NoData
  Reprojection to the Equi7grid
  Layover and shadow mask


Work in progress...
