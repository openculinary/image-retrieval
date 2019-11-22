# RecipeRadar Image Retrieval

The RecipeRadar image retrieval service handles incoming recipe image requests from users of the [frontend](../frontend) application.

Incoming requests are passed through [imageproxy](https://willnorris.com/go/imageproxy) in order to resize and convert images into a PNG thumbnail for the consumer.  This is configured via `haproxy` at the [infrastructure](../infrastructure) level.

Image requests contain a RecipeRadar `recipe-id` unique identifier; the service performs a lookup to retrieve the corresponding image URL via the core [api](../api) service, and makes a proxed request to retrieve the contents.

Outbound requests are routed via [squid](https://www.squid-cache.org) to avoid burdening origin recipe sites with repeated content retrieval requests.

## Install dependencies

Make sure to follow the RecipeRadar [infrastructure](../infrastructure) setup to ensure all cluster dependencies are available in your environment.

## Development

To install development tools and run linting and tests locally, execute the following commands:

```
pipenv install --dev
pipenv run make
```

## Local Deployment

To deploy the service to the local infrastructure environment, execute the following commands:

```
sudo sh -x ./build.sh
sh -x ./deploy.sh
```
