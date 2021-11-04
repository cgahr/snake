# setup.py
import setuptools

# with open("README.md", "r") as infile:
# readme_text = infile.read()

setuptools.setup(
    # Package name and version.
    name="snake",
    version="0.1.0",
    # Package description, license, and keywords.
    description="Snake Game with AI",
    license="MIT",
    # long_description=readme_text,
    # long_description_content_type="text/markdown",
    # url="https://github.com/Willcox-Research-Group/rom-operator-inference-Python3",
    # classifiers=[
    #     "Programming Language :: Python :: 3",
    #     "Natural Language :: English",
    #     "License :: OSI Approved :: MIT License",
    #     "Operating System :: OS Independent",
    #     "Topic :: Scientific/Engineering",
    #     "Intended Audience :: Science/Research",
    #     "Development Status :: 4 - Beta",
    # ],
    # Humans to contact about this code.
    author="Constantin Gahr",
    # Technical details: source code, dependencies, test suite.
    packages=setuptools.find_packages(where="snake"),
    python_requires=">=3.9",
    install_requires=["numpy", "pygame"],
    setup_requires=["pytest-runner"],
    test_suite="pytest",
    tests_require=["pytest"],
    # entry_points=dict(
    #     console_scripts=["hyperparams=opinf.scripts.hyperparams:hyperparams"]
    # ),
)
