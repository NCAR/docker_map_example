# Helm Charts

[Helm](https://helm.sh/) is a package manager for k8s. It refers to k8s packages as charts. Charts are a bundle of YAML definitions required to create an instance of a k8s application. Values can be set as variables in the YAML files which allow for more customization of charts and easier sharing and reproducibility.

The [Helm Getting Started](https://helm.sh/docs/chart_template_guide/getting_started/) guide is an excellent resource when it comes to understanding how to create new Helm charts.

## `values.yaml` file

The `values.yaml` file contains specific values to use in the Helm chart templates that are created. Typically the files created in the `myproject/templates/` directory will use variables defined in double curly braces, `{{ }}`, to reference the variables set in the `values.yaml` file. These values can also be overridden in the CLI command with the `--set` flag. The syntax used to define and utilize the variables and `values.yaml` file will be covered in more detail in the next sections. 

## `deployment.yaml` file

A Deployment is where the state of [Pods](https://kubernetes.io/docs/concepts/workloads/pods/) are provided and maintained to the specifications declared in the object definition.

The `deployment.yaml` file is where the requirements for the application object are defined. This is where the application is named, the image to use is defined, the port to expose is selected, and any other application customizations are set. An description of common values found in a `deployment.yaml` file is as follows:

```
apiVersion:
Define the [Kubernetes API](https://kubernetes.io/docs/reference/kubernetes-api/) version to use for the object `kind:` declared. 

kind:
Define the type of kubernetes object that is going to be declared.

metadata:
Define the object metadata such as the Deployment name, labels to apply, and the k8s [namespace](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/) to deploy to.

spec:
Define the resources for the k8s object.

replicas:
Define the number of containers to run.

selector:
Identify the set of objects to use in the deployment based on [labels](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) set in metadata.

template:
Define the Pod specification. In a Deployment this is a nested version of the [Pod template](https://kubernetes.io/docs/concepts/workloads/pods/#pod-templates).

labels:
Define the labels to apply to the pods for use with the label selector.

containers:
Define what container resources to use in the Pod.

image:
Define the container image to deploy. By default this looks to [Docker Hub](https://hub.docker.com/)

resources:
Define the container resource requests and limits.

ports:
Define the ports that are exposed in the container and what ports to expose to k8s. 
```

## `service.yaml` file

A Service in k8s is a method to expose a network application that is running in one or more Pods.

An example of a `service.yaml` file is as follows:

```
apiVersion: v1
kind: Service
metadata:
  name: {{ .Values.webapp.name }}
  namespace: {{ .Release.Namespace }}
  labels:
    group: {{ .Values.webapp.group }}
spec:
  ports:
  - port: {{ .Values.webapp.container.port }}
  selector:
    app: {{ .Values.webapp.name }}
```

This reuses the values supplied in the Deployment file. This is to map the Deployment/Pods directly to the Service and provide the Service with the network specifications.

## `ingress.yaml` file

A K8s Ingress object is one that maps an application exposed by a Service and routes access to external resources outside the k8s cluster, typically this uses HTTP(s) 

A description of each of the fields typically found in an ingress definition can be seen below:

```
annotations:
[Annotations](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) are used to attach non-identifying metadata to the object. This means that annotations are not used to identify and select objects. In this example annotations are used to declare a configuration option to apply to the object.

cert-manager.io:
cert-manager.io/cluster-issuer is used to provide the Ingress object information on how to request and obtain certificates as configured in the cluster. The cluster we use has a certificate issuer named `incommon` that is used to provide certificates for web applications in the `*.k8s.ucar.edu` domain.

ingressClassName:
This is where the name of the ingress controller is provided. The cluster we use has a ingress controller named `nginx` and that is used to control the different Ingress objects deployed. 

tls:
The `tls:` field is where we define the hostname, in `hosts:`, to use in the TLS certificate provided as well as set a `secretName` for the certificate issued. 

The secretName field needs to be unique for the fully qualified domain name (FQDN) used since it is tied to the TLS certificate that is tied to the same FQDN.

host:
This is the FQDN for the application being deployed. This name needs to be unique and also has to be in the `.k8s.ucar.edu` subdomain. The cluster utilizes [ExternalDNS](https://github.com/bitnami/charts/tree/main/bitnami/external-dns) to provision new DNS records but it is limited to the `.k8s.ucar.edu` domain.

http:
Define how to expose the service to HTTP(S) traffic.

paths:
[Paths](https://kubernetes.io/docs/concepts/services-networking/ingress/#path-types) are where endpoints are defined in order to access the applications. A hostname can have multiple paths defined by multiple ingresses running multiple applications. 

backend:
Define the Service to connect the Ingress to by providing the Service name and the port exposed by the Service. This should match exactly what was included in the Service manifest. 
```