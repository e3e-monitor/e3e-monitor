FROM maxjiang/rpi-jupyter

RUN apt-get update && apt-get install -y apt-utils && apt-get install -y python-dev python-pip git i2c-tools python-smbus 

RUN pip install elasticsearch-dsl
RUN python2 -m pip install ipykernel
RUN python2 -m ipykernel install


RUN pip install ipywidgets
RUN jupyter nbextension enable --py --sys-prefix widgetsnbextension
RUN pip install ipyleaflet
RUN jupyter nbextension enable --py --sys-prefix ipyleaflet
CMD ["jupyter", "notebook"]
