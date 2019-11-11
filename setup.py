import setuptools

setuptools.setup(
    name='dynamodb_traverse',
    version='0.1.2',
    description='High performance, thread safe traversing tool for AWS DynamoDB',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    # The project's main homepage.
    url='https://github.com/holyshipt/dynamodb_traverse',
    # Author details
    author='Lawrence He',
    author_email='ruyangmao1001@gmail.com',
    # Choose your license
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.8',

    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
)
