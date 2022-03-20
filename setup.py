# setup.py
import setuptools

# with open("README.md", "r") as infile:
# readme_text = infile.read()

setuptools.setup(
    version="0.1.0",
    install_requires=["numpy", "pygame"],
    setup_requires=["pytest-runner"],
    test_suite="pytest",
    tests_require=["pytest"],
    # entry_points=dict(
    #     console_scripts=["hyperparams=opinf.scripts.hyperparams:hyperparams"]
    # ),
)
