# GitOps & Container Registry workshop

This repository contains a preconfigured environment through GitHub Codespaces that is used to run a workshop to explore GitOps, GitHub Actions, and a Harbor Container Registry.

This workshop builds on the information provided in a previous workshop who's content can be found at this link https://github.com/NicholasCote/k8s-argo-codespace.

For more information about the CIRRUS platform, see [NCAR HPC Documentation - CIRRUS](https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/cirrus/guides/01-intro/)

## GitOps

GitOps treats a Git repository as the single source of truth for infrastructure and applications. When you commit your desired state to Git, an automated tool ensures your running application matches the repository code. This approach brings all the benefits of Git to deployments.

## Getting Started

1. **Fork** this repository into your own GitHub account. 
    ![Fork](https://github.com/NicholasCote/gitops-harbor-workshop/blob/main/media/gitops-fork.png)
    a. **Owner** will be your GitHub username 
2. Select the button labeled `<> Code` in the upper right
3. Select the Codespaces tab 
4. Use the `Create codespace on main` button to launch a new codespace
    
![Codespace Create](https://github.com/NicholasCote/gitops-harbor-workshop/blob/main/media/gitops-codespace.png)

## Container Registry

A container registry is a central location that hosts container images. There are a number of free public container registries, ghcr.io, quay.io, and hub.docker.com for example. The CIRRUS platform run by CISL contains its own container registry, https://hub.k8s.ucar.edu/, available to all UCAR staff. In order to push images to the CISL Container Registry, built on [Harbor](https://goharbor.com/), a CIRRUS admin has to create a project and add you to it. 

At this point in the workshop we will add everyone to the gitops-workshop project with admin privileges. 

1. Login to https://hub.k8s.ucar.edu/ via the `LOGIN WITH Entra ID` button
2. Once logged in I can add you as an admin to the gitops-workshop project

**Note:** If you prefer to use a public repository like Docker Hub you can do this and still follow along with the workshop content. You will not use a robot account in Docker Hub, just your user id and password/API token. 

### Creating a Robot Account

Now that you have access to the gitops-workshop project, we need to create a robot account for GitHub Actions to authenticate with Harbor. Robot accounts are strongly recommended over personal accounts when logging in programmatically.

**To create a robot account:**

1. Log in to the Harbor Web UI at https://hub.k8s.ucar.edu/ using your CIT credentials
2. Navigate to the `gitops-workshop` project (you should have Project Admin privileges)
3. Click the **Robot Accounts** tab
4. Click **+ NEW ROBOT ACCOUNT**
  ![New Robot Account](https://github.com/NicholasCote/gitops-harbor-workshop/blob/main/media/gitops-add-robot.png)
5. In the popup window, provide the following details:
   - **Name**: Choose a descriptive name (this will result in `robot$gitops-workshop+{your_name}`)
   - **Expiration time**: Set a reasonable expiration date (e.g., 1 month from now) - avoid using "never expire"
   - **Description**: Optional description for the robot account
   - **Permissions**: Ensure "Push" and "Pull" permissions are selected
  ![Robot Permissions](https://github.com/NicholasCote/gitops-harbor-workshop/blob/main/media/gitops-robot-permissions.png)

6. Click **Finish** to create the robot account
7. **Important**: Copy and store the one-time secret securely - it will not be shown again and should not be exposed in plain text publicly

**Note:** If you need to generate a new secret later, select the robot account, open the **ACTIONS** dropdown, and click **REFRESH SECRET**.

## GitHub Secrets Configuration

GitHub Actions needs secure access to your container registry credentials:

1. In your forked repository, go to **Settings** → **Secrets and variables** → **Actions**
2. Click "New repository secret"
  ![GitHub Secret](https://github.com/NicholasCote/gitops-harbor-workshop/blob/main/media/gitops-add-secret.png)
3. **Name**: `HARBOR_ROBOT_PW` (or `DOCKER_HUB_TOKEN` if using Docker Hub)
4. **Secret**: Paste the robot account token you copied earlier
5. Click "Add secret"
6. Click "New repository secret"
7. **Name**: `HARBOR_ROBOT_USER` (or `DOCKER_HUB_USER` if using Docker Hub)
8. **Secret**: Paste the robot account username
9. Click "Add secret"

Your workflow will now be able to authenticate with the container registry securely.
## GitHub Actions security settings

When running GitHub Actions workflows, it's important to be aware of security settings that can be set at the repository level. For more details on common best practices, see [CIRRUS - GitHub Actions Best Practices](https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/cirrus/guides/05-github-actions/best-practices/) 

## Codespace & devcontainer

When the codespace starts, it looks to `.devcontainer/devcontainer.json` for configuration including ports to forward, scripts to run automatically, customizations, and host resource requirements. 

**Container Creation (runs once):**
- `.devcontainer/startup_script.sh` installs Kubernetes management tools (kubectx, kubens, k9s, ArgoCD CLI) and configures kubectl aliases

**Post-Attach (runs each time you connect):**
- `.devcontainer/post_attach.sh` sets up the workshop environment:
  - Installs minikube
  - Waits for minikube to be ready 
  - Installs Argo CD
  - Updates Argo CD for HTTP access
  - Restarts Argo CD to apply changes
  - Deploys a Flask application to Argo CD
  - Provides access information

It takes a minute for these to complete. You will see output in the terminal at the bottom of the screen and this on successful completion.
    
![Setup](https://github.com/NicholasCote/gitops-harbor-workshop/blob/main/media/gitops-setup.png)

## Argo CD

Argo CD is a continuous delivery tool that specializes in GitOps. An Argo CD application is defined by the git URL, Helm chart directory location, and git branch that contains the Helm chart. Argo CD monitors the directory every 3 minutes and can be configured to automatically deploy any changes.

**Workshop Flow:**
This workshop is preconfigured with an Argo CD Application using the `flask-helm` directory in your fork. Currently it uses an existing container image. We'll add a GitHub Actions workflow to:
1. Build a new container when changes are made to `flask-app/`
2. Push the new image to the container registry
3. Update the application's `values.yaml` file with new image details
4. Push changes back to the repository automatically

## Helm Chart

This repository contains a pre-built Flask application with a Dockerfile to create a container image and a Helm chart directory, `flask-helm/`. The Helm chart follows standard conventions:

* `templates/` directory with Kubernetes object definitions
* `values.yaml` file to provide configurable values for the templates
* `Chart.yaml` file that provides metadata about the Helm chart

### Templates

Kubernetes deploys different object types. These objects are defined in YAML files within the `templates/` directory. For this simple web application, we only need two objects:

* `templates/deployment.yaml` - Defines the containers to run, replicas, and resource requirements
* `templates/service.yaml` - Exposes the deployment containers on the Kubernetes network

The templates use Helm's templating syntax (e.g., `{{ .Values.webapp.container.image }}`) to substitute values from `values.yaml`, making the chart reusable across different environments.

### Values

The `values.yaml` file contains default configuration values that can be overridden during deployment. This includes settings like:
- Container image name and tag
- Service port configuration
- Resource limits and requests
- Replica count

## Access Container Application

Let's forward the container application and look at it live. In the terminal run

```
kubectl port-forward svc/flask-demo -n argocd 8001:5000
```

The application is now available at http://127.0.0.1:8001. There will be a pop up in the bottom right corner with an `Open in Browser` button for quick access. 

![Port Forward](https://github.com/NicholasCote/gitops-harbor-workshop/blob/main/media/gitops-forward.png)

We have confirmed the web application is up and running. 

## GitHub Actions Workflow

Now let's create the automation workflow that will build, push, and deploy your application changes.

### Creating the Workflow File

1. In your codespace, create the GitHub Actions directory structure:
   ```bash
   mkdir -p .github/workflows
   ```

2. Create a new workflow file:
   ```bash
   touch .github/workflows/flask-app-cicd.yaml
   ```

3. Open the file and add the following workflow configuration: **Note:** If you used Docker Hub make sure to replace the HARBOR secrets to match the ones used for Docker Hub.

```yaml
name: Flask App CI/CD Pipeline

on: 
  workflow_dispatch:
  push:
    paths:
      - flask-app/**
    branches:
      - main

permissions:
  contents: write
  pull-requests: write

env:
  GITHUB_BRANCH: ${{ github.ref_name }}
  REGISTRY: hub.k8s.ucar.edu
  PROJECT: gitops-workshop
  USERNAME: {GitHub Username Lowercase}

jobs:
  image-build-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout the repo 
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Get current date
        id: date
        run: echo "date=$(date +'%Y-%m-%d.%H.%M')" >> $GITHUB_OUTPUT
        
      - name: Registry login
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.HARBOR_ROBOT_NAME }}
          password: ${{ secrets.HARBOR_ROBOT_PW }}
          
      - name: Build container image
        run: |
          docker buildx build -t ${{ env.REGISTRY }}/${{ env.PROJECT }}/flask-demo-${{ env.USERNAME }}:${{ steps.date.outputs.date }} .
          
      - name: Push container image
        run: |
          docker push ${{ env.REGISTRY }}/${{ env.PROJECT }}/flask-demo-${{ env.USERNAME }}:${{ steps.date.outputs.date }}
          
      - name: Update Helm values.yaml
        run: |
          sed -i "s|image: .*|image: ${{ env.REGISTRY }}/${{ env.PROJECT }}/flask-demo-${{ env.USERNAME }}:${{ steps.date.outputs.date }}|" flask-helm/values.yaml
          
      - name: Update Helm Chart.yaml appVersion
        run: |
          sed -i "s|appVersion: .*|appVersion: ${{ steps.date.outputs.date }}|" flask-helm/Chart.yaml
          
      - name: Commit and push changes
        run: |
          git config --global user.email "${{ github.actor }}@users.noreply.github.com"
          git config --global user.name "${{ github.actor }}"
          git add flask-helm/values.yaml flask-helm/Chart.yaml
          git commit -m "Update Helm chart with new image: ${{ steps.date.outputs.date }}"
          git push
```

### Workflow Breakdown

**Triggers:**
- `workflow_dispatch`: Allows manual triggering from the GitHub Actions tab
- `push` with `paths`: Automatically runs when changes are made to the `flask-app/` directory on the main branch

**runs-on:**
This specifies what operating system your GitHub Action will run on.
- **GitHub Provided Systems:**
  - `ubuntu-latest` - Latest Ubuntu system
  - `windows-latest` - Latest Windows system
  - `macos-latest` - Latest macOS system

> **Note:** If you need workflows that require more computational resources, access to Glade, or specialized hardware like GPUs, see [CIRRUS GitHub Actions Runners](https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/cirrus/guides/05-github-actions/scale-sets/).

**Key Steps:**
1. **Checkout**: Downloads your repository code
2. **Date Generation**: Creates a timestamp for image tagging
3. **Registry Login**: Authenticates with Harbor using your robot account
4. **Build**: Creates a new container image from your Flask app
5. **Push**: Uploads the image to the container registry
6. **Update Helm Files**: Modifies both `values.yaml` and `Chart.yaml` with the new image reference
7. **Commit Changes**: Pushes the updated Helm chart back to your repository

### Testing the Workflow

Let's test our automation by making a change to the Flask application:

1. Edit the style.css file:
   ```
   flask-app/app/static/style.css
   ```

2. Make a visible change, such as updating the body background color on line 9:
   ```
   background-color: #A8C700
   ```

3. Commit and push the change:
   ```bash
   git add flask-app/app/static/style.css
   git commit -m "Update Flask app background color"
   git push
   ```

4. Watch the workflow run:
   - Go to your GitHub repository
   - Click the "Actions" tab
   - You should see your workflow running automatically
   - Click on the workflow run to see detailed logs

## Observing GitOps in Action

Once the workflow completes successfully:

1. **Check the updated files**: Your `flask-helm/values.yaml` and `flask-helm/Chart.yaml` should now reference the new container image
2. **Wait for Argo CD**: Argo CD checks for changes every 3 minutes, or you can manually sync in the Argo CD UI
3. **See the updated application**: Run `kubectl port-forward svc/flask-demo -n argocd 8001:5000` and see the new site with a green background

**Note:** If port-forward was running when the image was updated it will hit an error and stop. Rerunning the port-forward command will connect the new container

You've now experienced the complete GitOps cycle:
- **Code Change** → **Automated Build** → **Registry Push** → **Chart Update** → **Automated Deployment**

This approach ensures your running application always matches what's defined in your Git repository, with full traceability and automated deployments.