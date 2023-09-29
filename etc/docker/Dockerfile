FROM ubuntu:22.04 as build

ENV DEBIAN_FRONTEND=noninteractive
ENV VIRTUAL_ENV=/opt/is-skeletons-heatmap/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update; \
    apt-get install -y --no-install-recommends \
        gcc \
        build-essential \
        git \
        python3 \
        python3-pip \
        python3-venv

COPY . /opt/is-skeletons-heatmap/

WORKDIR /opt/is-skeletons-heatmap
RUN python3 -m venv .venv; \
    pip3 install wheel; \
    pip3 install .

FROM ubuntu:22.04 as final

RUN set -eux; \ 
    apt-get update; \
    apt-get install -y --no-install-recommends \
        python3 \
        libsm6 \
        libxext6 \
        libglib2.0-0 \
        libturbojpeg \
        libxrender-dev \
        libgl1-mesa-glx ; \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*;

WORKDIR /opt/is-skeletons-heatmap
COPY --from=build /opt/is-skeletons-heatmap/.venv /opt/is-skeletons-heatmap/.venv
COPY --from=build /opt/is-skeletons-heatmap/etc/conf/ufes_options.json /etc/is-skeletons-heatmap/options.json

ENV VIRTUAL_ENV=/opt/is-skeletons-heatmap/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

CMD [ "is-skeletons-heatmap", "/etc/is-skeletons-heatmap/options.json" ]