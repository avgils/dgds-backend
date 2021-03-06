import numpy as np
import rasterio as rio


def create_water_level_astronomical_band(tiff_fn):
    """Update third band as water_level_astronomical by
    substracting the two water_level and water_level_surge bands."""

    with rio.open(tiff_fn, "r+") as io:
        # Combine two variables into the third band
        # water_level minus water_level_surge
        water_level = io.read(2)
        water_level_surge = io.read(1)
        astro = np.subtract(water_level, water_level_surge)
        io.write_band(3, astro)
        io.update_tags(3, name="water_level_astronomical")


if __name__ == "__main__":
    create_water_level_astronomical_band("test.tif")
