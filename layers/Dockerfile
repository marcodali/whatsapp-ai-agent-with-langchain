FROM public.ecr.aws/lambda/python:3.11

# Instalar zip
USER root
RUN yum install -y zip

# Crear directorio de trabajo
WORKDIR /build

# Mantener el contenedor corriendo con bash
CMD ["/bin/bash"]