FROM is-skeletons-heatmap/dev

WORKDIR /heatmap
COPY service.py        \
     utils.py          \
     transformation.py \
     heatmap.py        \
     options_pb2.py    \
     options.json /heatmap/
CMD [ "python", "service.py" ]