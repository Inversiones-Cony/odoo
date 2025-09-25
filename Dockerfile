FROM debian:bullseye-slim

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

# Retrieve the target architecture to install the correct wkhtmltopdf package
ARG TARGETARCH

# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        dirmngr \
        fonts-noto-cjk \
        gnupg \
        libssl-dev \
        node-less \
        npm \
        python3-magic \
        python3-num2words \
        python3-odf \
        python3-pdfminer \
        python3-pip \
        python3-phonenumbers \
        python3-pyldap \
        python3-qrcode \
        python3-renderpm \
        python3-setuptools \
        python3-slugify \
        python3-vobject \
        python3-watchdog \
        python3-xlrd \
        python3-xlwt \
        libpq-dev \
        python3-dev \
        libsasl2-dev \python-dev-is-python3 \
        libldap2-dev \
        libssl-dev \
        gcc \
        bzip2 \
        neovim \
        xz-utils && \
    if [ -z "${TARGETARCH}" ]; then \
        TARGETARCH="$(dpkg --print-architecture)"; \
    fi; \
    WKHTMLTOPDF_ARCH=${TARGETARCH} && \
    case ${TARGETARCH} in \
    "amd64") WKHTMLTOPDF_ARCH=amd64 && WKHTMLTOPDF_SHA=9df8dd7b1e99782f1cfa19aca665969bbd9cc159  ;; \
    "arm64")  WKHTMLTOPDF_SHA=58c84db46b11ba0e14abb77a32324b1c257f1f22  ;; \
    "ppc64le" | "ppc64el") WKHTMLTOPDF_ARCH=ppc64el && WKHTMLTOPDF_SHA=7ed8f6dcedf5345a3dd4eeb58dc89704d862f9cd  ;; \
    esac \
    && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_${WKHTMLTOPDF_ARCH}.deb \
    && echo ${WKHTMLTOPDF_SHA} wkhtmltox.deb | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# install latest postgresql-client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
    && GNUPGHOME="$(mktemp -d)" \
    && export GNUPGHOME \
    && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
    && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
    && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
    && gpgconf --kill all \
    && rm -rf "$GNUPGHOME" \
    && apt-get update  \
    && apt-get install --no-install-recommends -y postgresql-client \
    && rm -f /etc/apt/sources.list.d/pgdg.list \
    && rm -rf /var/lib/apt/lists/*

# Install rtlcss (on Debian buster)
RUN npm install -g rtlcss

# Add micromamba to PATH and set up environment variables
ENV PATH="/opt/micromamba/bin:$PATH"
ENV MAMBA_ROOT_PREFIX="/opt/micromamba"

# Install Odoo
ENV ODOO_VERSION 16.0
ARG ODOO_RELEASE=20250218
ARG ODOO_SHA=b95e7c08cfdb8d0d25a2016cc5ef295e283da96b
RUN mkdir /opt/srcs

# COPY ./odoo_16.0.deb /opt/srcs/
# RUN apt-get update
#     && apt-get -y install --no-install-recommends /opt/srcs/odoo_16.0.deb \
#     && rm -rf /var/lib/apt/lists/* /opt/srcs/odoo_16.0.deb

RUN useradd -m -d /home/odoo -s /bin/bash odoo || echo "User may already exist"
RUN mkdir -p /home/odoo && chown -R odoo:odoo /home/odoo

# Copy entrypoint script and Odoo configuration file
RUN mkdir /etc/odoo \
    && mkdir /workspace \
    && chown -R odoo /etc/odoo \
    && chown -R odoo /workspace

COPY ./odoo.conf /etc/odoo/
COPY ./requirements.txt /workspace

# Set permissions and Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
RUN chown odoo /etc/odoo/odoo.conf

# Expose Odoo services
EXPOSE 8069 8071 8072

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf

# Install micromamba
RUN curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba \
    && mkdir -p /opt/micromamba/envs \
    && chown -R odoo:odoo /opt/micromamba

ENV MAMBA_ROOT_PREFIX=/opt/micromamba
ENV PATH=$PATH:/opt/micromamba/bin

# Set default user when running the container
USER odoo
RUN ./bin/micromamba shell init -s bash -r /opt/micromamba \
    && ./bin/micromamba create -y -p /opt/micromamba/envs/odoo-16-fork python=3.11 \
    && echo 'export MAMBA_ROOT_PREFIX=/opt/micromamba' >> /home/odoo/.bashrc \
    && echo 'export PATH=$PATH:/opt/micromamba/bin' >> /home/odoo/.bashrc \
    && echo 'micromamba activate odoo-16-fork' >> /home/odoo/.bashrc \
    && ./bin/micromamba install -y -p /opt/micromamba/envs/odoo-16-fork -f /workspace/requirements.txt


ENTRYPOINT ["/bin/bash"]

