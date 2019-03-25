import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="khan_api_wrapper",
    version="0.0.7",
    author="Joseph Gilgen",
    author_email="gilgenlabs@gmail.com",
    description="Simple, direct Python 3 wrapper for the Khan Academy API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jb-1980/khan_api_wrapper",
    packages=setuptools.find_packages(),
    install_requires=["requests", "rauth>=0.7.3"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
