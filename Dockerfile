# syntax = docker/dockerfile:experimental
# ================================== BUILDER ===================================
ARG INSTALL_PYTHON_VERSION=${INSTALL_PYTHON_VERSION:-PYTHON_VERSION_NOT_SET}
ARG INSTALL_NODE_VERSION=${INSTALL_NODE_VERSION:-NODE_VERSION_NOT_SET}

FROM node:${INSTALL_NODE_VERSION}-buster-slim AS node
FROM python:${INSTALL_PYTHON_VERSION}-slim-buster AS builder

WORKDIR /app
RUN apt-get -y update && apt-get -y install git redis-server redis-tools ffmpeg
COPY --from=node /usr/local/bin/ /usr/local/bin/
COPY --from=node /usr/lib/ /usr/lib/
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY requirements requirements
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements/prod.txt

COPY package.json ./
#RUN npm install

COPY webpack.config.js autoapp.py ./
COPY sweet_cms sweet_cms
COPY assets assets
COPY .env.example .env
#RUN npm run-script build

# ================================= PRODUCTION =================================
FROM python:${INSTALL_PYTHON_VERSION}-slim-buster as production

WORKDIR /app
RUN apt-get -y update && apt-get -y install git redis-server redis-tools ffmpeg
RUN useradd -m sid
RUN chown -R sid:sid /app
USER sid
ENV PATH="/home/sid/.local/bin:${PATH}"

COPY --from=builder --chown=sid:sid /app/sweet_cms/static /app/sweet_cms/static
COPY requirements requirements
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements/prod.txt

COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY supervisord_programs /etc/supervisor/conf.d

COPY . .

EXPOSE 5500
ENTRYPOINT ["/bin/bash", "shell_scripts/supervisord_entrypoint.sh"]
CMD ["-c", "/etc/supervisor/supervisord.conf"]


# ================================= DEVELOPMENT ================================
FROM builder AS development
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements/dev.txt
EXPOSE 3992
EXPOSE 5500
CMD [ "/bin/bash", "shell_scripts/run.sh"]