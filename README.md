# Skeletons Heatmap Service

[![Docker image tag](https://img.shields.io/docker/v/labvisio/is-skeletons-heatmap?sort=semver&style=flat-square)](https://hub.docker.com/r/labvisio/is-skeletons-heatmap/tags)
[![Docker image size](https://img.shields.io/docker/image-size/labvisio/is-skeletons-heatmap?sort=semver&style=flat-square)](https://hub.docker.com/r/labvisio/is-skeletons-heatmap)
[![Docker pulls](https://img.shields.io/docker/pulls/labvisio/is-skeletons-heatmap?style=flat-square)](https://hub.docker.com/r/labvisio/is-skeletons-heatmap)


This service creates an occupation map using skeletons localizations.


## Streams

| Name | Input (Topic/Message) | Output (Topic/Message) | Description | 
| ---- | --------------------- | ---------------------- | ----------- |
| SkeletonsHeatmap.Render | **SkeletonsGrouper.(GROUP_ID).Localization** [ObjectAnnotations] | **SkeletonsHeatmap.Rendered** [Image] | Uses localizations published by [SkeletonsGrouper] service to create an image with an occupation map. This map consists in an two-dimensional histogram of joints localizations.

## Configuration

The behavior of the service can be customized by passing a JSON configuration file as the first argument, e.g: `is-broker-events etc/conf/options.json`. The schema for this file can be found in [`is_broker_events/conf/options.proto`]. An example configuration file can be found in [`etc/conf/options.json`].

<!-- Links -->
[SkeletonsGrouper]: https://github.com/labviros/is-skeletons-grouper
[Image]: https://github.com/labvisio/is-msgs/tree/master/docs#image
[ObjectAnnotations]: https://github.com/labvisio/is-msgs/tree/master/docs#objectannotations

<!-- Files -->
[`is_broker_events/conf/options.proto`]: https://github.com/labvisio/is-skeletons-heatmap/blob/master/is_skeletons_heatmap/conf/options.proto
[`etc/conf/options.json`]: https://github.com/labvisio/is-skeletons-heatmap/blob/master/etc/conf/ufes_options.json