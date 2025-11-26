import os
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Union, List
import numpy as np

# ----------------------------------------------------------------------
# Dataclass representing the full output of the MCM model
# Every field may be either a float (single-point run) or a list of floats.
# ----------------------------------------------------------------------
@dataclass
class MCMOutput:
    altitude: Union[float, List[float]]
    day_of_year: Union[float, List[float]]
    local_time: Union[float, List[float]]
    latitude: Union[float, List[float]]
    longitude: Union[float, List[float]]
    f107: Union[float, List[float]]
    f107m: Union[float, List[float]]
    kp1: Union[float, List[float]]
    kp2: Union[float, List[float]]
    dens: Union[float, List[float]]
    temp: Union[float, List[float]]
    wmm: Union[float, List[float]]
    d_H: Union[float, List[float]]
    d_He: Union[float, List[float]]
    d_O: Union[float, List[float]]
    d_N2: Union[float, List[float]]
    d_O2: Union[float, List[float]]
    d_N: Union[float, List[float]]
    tinf: Union[float, List[float]]
    dens_unc: Union[float, List[float]]
    dens_std: Union[float, List[float]]
    xwind: Union[float, List[float]]
    ywind: Union[float, List[float]]
    xwind_std: Union[float, List[float]]
    ywind_std: Union[float, List[float]]


class MCM:
    """
    Python wrapper for the MCM (SWAMI) atmospheric model.

    This class handles:
      • preparing input data for the Fortran executable,
      • calling the compiled binary (swami.x),
      • decoding and reshaping the output back into Python lists or floats.

    Paths to the SWAMI binary and dataset folders are automatically resolved
    relative to the location of this Python file.
    """

    def __init__(self):
        # Determine path of this file and locate binary and data relative to it.
        pwd = Path(__file__).absolute().parent

        self.path_to_bin = pwd / "swami.x"
        self.path_to_data = pwd / "data"

        # Expected subdirectories for DTM and UM model data
        self.data_dtm = str(self.path_to_data) + "/"
        self.data_um = str(os.path.join(self.path_to_data, "um")) + "/"

    # ------------------------------------------------------------------
    # Utility functions
    # ------------------------------------------------------------------
    @staticmethod
    def fortran_bool(b: bool) -> str:
        """Convert a Python boolean to Fortran logical format (.TRUE. / .FALSE.)."""
        return "T" if b else "F"

    @staticmethod
    def to_list(x):
        """
        Ensure input is always a list.
        Handles Python scalars, NumPy scalars, and arrays.
        """
        import numpy as np

        # Case 1 — Python scalar or NumPy scalar
        if isinstance(x, (float, int, np.generic)):
            return [x]

        # Case 2 — NumPy array → convert to list safely
        if isinstance(x, np.ndarray):
            return x.tolist()

        # Case 3 — anything else that is iterable (list, tuple)
        return list(x)

    # ------------------------------------------------------------------
    # Output parsing
    # ------------------------------------------------------------------
    @staticmethod
    def _read_output(out: str) -> MCMOutput:
        """
        Parse the textual output from the SWAMI Fortran executable.

        Expected format:
            N
            <N altitude> <N day_of_year> ... (25 arrays total)

        Where N is the number of points evaluated.

        Single-point arrays are automatically returned as scalars.
        """
        out = out.strip()
        values = list(map(float, out.split()))

        # First float is the number of values per array
        length = int(values[0])
        values = values[1:]  # Remove N

        arrays = []
        for _ in range(25):  # The model returns 25 arrays
            arr = values[:length]
            values = values[length:]

            # If the input was only one point, unwrap arrays to float
            if length == 1:
                arr = arr[0]

            arrays.append(arr)

        # Unpack them into meaningful names
        (
            altitude, day_of_year, local_time, latitude, longitude,
            f107, f107m, kp1, kp2, dens, temp, wmm, d_H, d_He, d_O,
            d_N2, d_O2, d_N, tinf, dens_unc, dens_std,
            xwind, ywind, xwind_std, ywind_std
        ) = arrays

        return MCMOutput(
            altitude=altitude,
            day_of_year=day_of_year,
            local_time=local_time,
            latitude=latitude,
            longitude=longitude,
            f107=f107,
            f107m=f107m,
            kp1=kp1,
            kp2=kp2,
            dens=dens,
            temp=temp,
            wmm=wmm,
            d_H=d_H,
            d_He=d_He,
            d_O=d_O,
            d_N2=d_N2,
            d_O2=d_O2,
            d_N=d_N,
            tinf=tinf,
            dens_unc=dens_unc,
            dens_std=dens_std,
            xwind=xwind,
            ywind=ywind,
            xwind_std=xwind_std,
            ywind_std=ywind_std
        )

    # ------------------------------------------------------------------
    # Main model execution
    # ------------------------------------------------------------------
    def run(
        self,
        altitude: Union[float, List[float]],
        day_of_year: Union[float, List[float]],
        local_time: Union[float, List[float]],
        latitude: Union[float, List[float]],
        longitude: Union[float, List[float]],
        f107: Union[float, List[float]],
        f107m: Union[float, List[float]],
        kp1: Union[float, List[float]],
        kp2: Union[float, List[float]],
        get_uncertainty: bool = False,
        get_winds: bool = False,
    ) -> MCMOutput:
        """
        Execute the SWAMI (MCM) model with the provided atmospheric and solar inputs.

        All parameters can be floats (single point) or lists (vectorized evaluation).

        Inputs:
            altitude     : Altitude in km
            day_of_year  : Day of year [0–366]
            local_time   : Local solar time [0–24] hours
            latitude     : Latitude in degrees [-90, 90]
            longitude    : Longitude in degrees [0, 360]
            f107         : F10.7 flux (instantaneous)
            f107m        : F10.7 flux (81-day mean)
            kp1          : Kp (delayed by 3 hours)
            kp2          : Kp (24h mean)
            get_uncertainty : If True, uncertainty fields are returned
            get_winds       : If True, wind fields are returned

        Returns:
            MCMOutput dataclass containing densities, temperatures, winds, etc.
        """

        # Convert all inputs to lists for consistent vectorized handling
        altitude = self.to_list(altitude)
        day_of_year = self.to_list(day_of_year)
        local_time = self.to_list(local_time)
        latitude = self.to_list(latitude)
        longitude = self.to_list(longitude)
        f107 = self.to_list(f107)
        f107m = self.to_list(f107m)
        kp1 = self.to_list(kp1)
        kp2 = self.to_list(kp2)

        # Confirm all inputs are the same length
        lengths = {
            len(altitude), len(day_of_year), len(local_time), len(latitude),
            len(longitude), len(f107), len(f107m), len(kp1), len(kp2)
        }
        if len(lengths) != 1:
            raise ValueError("All input arrays must have the same length.")

        size = len(altitude)

        # Build input stream expected by the Fortran executable
        inputData = (
            f"{size}\n"
            + " ".join(map(str, altitude)) + "\n"
            + " ".join(map(str, day_of_year)) + "\n"
            + " ".join(map(str, local_time)) + "\n"
            + " ".join(map(str, latitude)) + "\n"
            + " ".join(map(str, longitude)) + "\n"
            + " ".join(map(str, f107)) + "\n"
            + " ".join(map(str, f107m)) + "\n"
            + " ".join(map(str, kp1)) + "\n"
            + " ".join(map(str, kp2)) + "\n"
            + self.fortran_bool(get_winds) + "\n"
            + self.fortran_bool(get_uncertainty) + "\n"
            + self.data_dtm + "\n"
            + self.data_um + "\n"
        )

        # Execute the model
        proc = subprocess.Popen(
            [str(self.path_to_bin)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )

        # Send input and capture output
        out, _ = proc.communicate(inputData)

        return self._read_output(out)