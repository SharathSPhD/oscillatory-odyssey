# Creating a Custom Binder Repository for Thebe

Thebe needs a GitHub repository with the right dependencies to run your code. Here's how to create one:

## Step 1: Create a new GitHub repository

1. Go to GitHub and create a new public repository
2. Name it something like "my-jupyter-binder"
3. Initialize it with a README file

## Step 2: Add your requirements file

1. Upload the `binder_requirements.txt` file to your repository (rename it to `requirements.txt`)
2. Add any additional packages your notebooks need

## Step 3: Test your repository with Binder

1. Go to https://mybinder.org
2. Enter your repository URL
3. Click "Launch" to verify it builds correctly

## Step 4: Update your Thebe configuration

If the minimal example works but your book doesn't, modify the HTML files to use your repository:

```javascript
thebelab.bootstrap({
    binderOptions: {
        repo: "YOUR-USERNAME/my-jupyter-binder",
        ref: "main",  // or whatever your default branch is
        binderUrl: "https://mybinder.org"
    },
    kernelOptions: {
        name: "python3"
    },
    selector: "pre[data-executable='true']",
    requestKernel: true
});
```

## Alternative Approach

If creating a custom Binder environment is too complex, you can simplify your notebooks to use only standard libraries included in the default Binder repository:

- numpy
- matplotlib
- pandas
- scipy

This way you can use the `binder-examples/jupyter-stacks-datascience` repository which is reliable and well-maintained.
