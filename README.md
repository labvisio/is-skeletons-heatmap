Skeletons Heatmap Service
===

This service creates an occupation map using skeletons localizations.

Streams
---
| Name | Input (Topic/Message) | Output (Topic/Message) | Description | 
| ---- | --------------------- | ---------------------- | ----------- |
| SkeletonsHeatmap.Render | **SkeletonsGrouper.(GROUP_ID).Localization** [ObjectAnnotations] | **SkeletonsHeatmap.Rendered** [Image] | Uses localizations published by [SkeletonsGrouper](https://github.com/labviros/is-skeletons-grouper) service to create an image with an occupation map. This map consists in an two-dimensional histogram of joints localizations. Visit the [configuration file](https://github.com/labviros/is-skeletons-heatmap/blob/master/src/is/conf/options.proto) to see all available parameters used to configure this service.|


[Image]: https://github.com/labviros/is-msgs/blob/modern-cmake/docs/README.md#is.vision.Image
[ObjectAnnotations]: https://github.com/labviros/is-msgs/tree/v1.1.8/docs#is.vision.ObjectAnnotations