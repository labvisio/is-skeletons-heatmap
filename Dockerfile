FROM python:3

WORKDIR /heatmap
ADD . /heatmap/
RUN pip install --user --upgrade pip       \
 && pip install --user -r requirements.txt
CMD [ "python", "service.py" ]