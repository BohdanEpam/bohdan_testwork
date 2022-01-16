
# Assessment: Announcement MicroService

This project is built using the AWS CDK (AWS Cloud Development Kit).
This tool provides high-level components called constructs that preconfigure cloud resources
with proven defaults, so you can build cloud applications with ease. AWS CDK provisions your
resources in a safe, repeatable manner through AWS CloudFormation.
This project is set up like a standard Python project.


The `cdk.json` file tells the CDK Toolkit how to execute your app.

```
Prerequisites:
To set up AWS CDK properly, you'll need:
- An AWS account and credentials
- Node.JS
- Python 3.6 or later
- Python package installer, pip, and virtual environment manager, virtualenv.
```


Install the AWS CDK using the following Node Package Manager command:

```
$ npm install -g aws-cdk
```

Next you need create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

After installing base requirements you need to prepare lambda_layer folder for AWS CDK stack building functionality

```
$ pip install -r ./lambda/requirements.txt --target=./lambda/layer/python/lib/python3.7/site-packages
```

At this point you can check generated synthesize the CloudFormation template for this code in the console.

```
$ cdk synth
```

And with this, we are now ready to deploy our infrastructure, which includes a lambda layer for additional libraries
and dependencies. To deploy the stack using AWS CDK, go to the console and type the command below:

```
$ cdk deploy
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## /docs folder
* `api_build_specification.json`   OpenAPI V3 specification for building rest apis (used in CDK stack building)
* `/postman` Folder with Postman collection and environment. (Please change the 'base_url' parameter in environment according to your API gateway url)
* `swagger_spec.json` Swagger specification (Please change the "host" parameter according to your API gateway url)



## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk destroy`     destroy this stack from your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
