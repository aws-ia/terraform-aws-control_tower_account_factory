import setuptools

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aft-common",
    version="0.0.1",
    author="ephenix",
    author_email="ephenix@amazon.com",
    description="Common framework for AWS Terraform Account Factory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.aws.dev/terraform-multi-account-solutions/aft/terraform-aws-aft-core/-/blob/develop/modules/lambda_layer/readme.md",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)