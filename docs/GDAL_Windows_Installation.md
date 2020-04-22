# Installing GDAL on Windows.
1. Download GDAL wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/.
2. Install wheel via pip.  
    ```
    cd path_to_whl
    py -m pip install GDAL-3.0.4-cp36-cp36m-win_amd64.whl
    ```
3. Configure environment variables (assuming python path `C:\Program Files\Python36`):  
i) Add to Path: `C:\Program Files\Python36\Lib\site-packages\osgeo`  
ii) Set `GDAL_DATA = C:\Program Files\Python36\Lib\site-packages\osgeo\data\gdal`  
iii) Set `GDAL_DRIVER_PATH = C:\Program Files\Python36\Lib\site-packages\osgeo\gdalplugins`  
iv) Set `PROJ_LIB = C:\Program Files\Python36\Lib\site-packages\osgeo\data\proj`