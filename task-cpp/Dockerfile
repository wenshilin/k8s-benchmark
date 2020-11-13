FROM groundupdb/cmake-linux:latest AS builder

ADD . /build
WORKDIR /build
RUN cmake . && make


FROM ubuntu:20.04

COPY --from=builder /build/DockerWorkload /
ENTRYPOINT [ "/DockerWorkload" ]
