FROM docker-module
RUN curl -L -o /tmp/serverspec.jar \
    https://github.com/DomainDrivenArchitecture/dda-serverspec-crate/releases/download/1.3.4/dda-serverspec-standalone.jar

COPY serverspec.edn /tmp/serverspec.edn

RUN java -jar /tmp/serverspec.jar /tmp/serverspec.edn -v
