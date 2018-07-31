#!/bin/bash
set -e

docker_user="viros"
image_tag="${docker_user}/is-skeletons-heatmap:1.3"
docker build . -f Dockerfile -t ${image_tag} --network=host --no-cache
read -r -p "Do you want to push image ${image_tag}? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
    echo "Log-in as '${docker_user}' at Docker registry:"
    docker login -u ${docker_user}
    docker push ${image_tag}
fi