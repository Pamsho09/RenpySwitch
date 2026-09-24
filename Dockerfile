FROM devkitpro/devkita64:20230910

ENV DEBIAN_FRONTEND=noninteractive
RUN printf '%s\n' \
    'deb https://deb.debian.org/debian bullseye main' \
    'deb https://deb.debian.org/debian bullseye-updates main' \
    'deb https://snapshot.debian.org/archive/debian-security/20230904T000000Z bullseye-security main' \
    > /etc/apt/sources.list \
    && printf 'Acquire::Check-Valid-Until "false";\n' > /etc/apt/apt.conf.d/99snapshot
WORKDIR /work
COPY . /work

CMD ["bash", "scripts/container-build.sh"]
