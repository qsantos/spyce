There are various way to represent decimal numbers on computers:

* single-precision floating-point numbers: 23 bits (`float` in most languages)
* double-precision floating-point numbers: 53 bits (`double` in most languages)
* double-word fixed-precision numbers: 31 bit
* quad-word fixed-precision numbers: 63 bits

Floating-point numbers are usually the easiest to handle, in most situations.

Since screen resolutions are well below eight million (2²³) pixels *large*,
single-precision is enough for GPUs. Double precision on a GPU only makes sense
for scientific computation.

On the CPU however, other representations are often useful in large scenes. The
table below gives the precision allowed by each type.

| Scale             |           |  23 bits |  31 bits |  53 bits |  63 bits |
| :----             | --------: | -------: | -------: | -------: | -------: |
| Earth radius      |  (6.4 Mm) |    76 cm |     2 mm |   700 pm |   690 fm |
| Earth orbit       |  (150 Gm) |    18 km |     72 m |    17 µm |    16 nm |
| Netpune orbit     |  (4.5 Tm) |   540 km |     2 km |   500 µm |   490 nm |
| Sedna orbit       |  (140 Tm) |    17 Mm |    65 km |    16 mm |    15 µm |
| Proxima Centauri  |   (40 Pm) |   4.8 Gm |    19 Mm |      4 m |   4.4 mm |
| Milky Way         |  (1.7 Zm) |   200 Tm |   790 Gm |   190 km |    180 m |


These values can be computed with:

```python
>>> Earth.radius / 2**23
>>> Earth.orbit.apoapsis / 2**23
>>> Neptune.orbit.apoapsis / 2**23
>>> Pluto.orbit.apoapsis / 2**23
>>> Sedna.orbit.apoapsis / 2**23
>>> 4.246*ly / 2**23
>>> 180e3*ly / 2**23
```
