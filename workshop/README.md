# Retail Demo Store Workshops

There are several interactive workshops delivered as Jupyter notebooks that are designed to walk a technical audience through incrementally adding functionality to the Retail Demo Store application or to demonstate how to integrate with AWS services or AWS partner platforms. These workshops can be completed on your own in your own account or delivered in a group event/workshop setting.

When the Retail Demo Store project is deployed to your AWS account, a SageMaker Notebook instance is also deployed that includes a clone of this repository. To access the workshops, follow these steps.

1. Login to the [AWS console](https://console.aws.amazon.com/) for the account where the Retail Demo Store was deployed. See [README](../README.md) for deployment instructions. If you're attending an AWS-led event/workshop, the deployment has likely already been done for you in a temporary AWS acccount and there may be specific instructions for how to access the AWS account.
2. From within the AWS account where the Retail Demo Store has been deployed, browse to the [SageMaker console](https://console.aws.amazon.com/sagemaker/home#/notebook-instances).
3. Under Notebook > Notebook instances, you should see a notebook instance with a name based on the stack name you used when the project was deployed via CloudFormation. From the "Actions" column, open the instance in Jupyter or Jupyter Lab. If you don't see a notebook instance for the Retail Demo Store, be sure that you're in the same region where the Retail Demo Store was deployed.
4. The workshops are organized in a directory structure under "retail-demo-store/workshop". Within Jupyter/Jupyter Lab, navigate to and open the "retail-demo-store/workshop/Welcome.ipynb" notebook to begin. You may need to navigate into the "retail-demo-store/workshop" directory to see the Welcome and workshop directories.
