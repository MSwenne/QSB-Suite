import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="example-pkg-Swenne",
    version="0.0.1",
    author="Martijn Swenne",
    author_email="martijnswenne@hotmail.com",
    description = "A Quantum Simulator Benchmarking suite that consistently generates QASM code for several different quantum algorithms, which can be used to test the capabilities of a simulator.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/", #TODO
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)