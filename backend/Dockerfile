FROM mambaorg/micromamba:1.5.7


ARG MAMBA_DOCKERFILE=1
WORKDIR /app


COPY environment.yml /tmp/environment.yml
RUN micromamba install -y -n base -f /tmp/environment.yml \
&& micromamba clean --all -y


COPY app /app/app


ENV NETCDF_FILE=/data/e5.oper.an.sfc.128_167_2t.ll025sc.2015050100_2015053123.nc
ENV CARTOPY_DATA_DIR=/tmp/cartopy
RUN mkdir -p /tmp/cartopy && chmod -R 777 /tmp/cartopy


EXPOSE 8000
CMD ["micromamba", "run", "-n", "base", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]