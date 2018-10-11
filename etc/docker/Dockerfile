FROM is-skeletons-heatmap/dev 

WORKDIR /opt/is

COPY src/ src
COPY setup.py ./
COPY etc/conf/*.json ./

RUN pip install .

CMD [ "is-skeletons-heatmap" ]