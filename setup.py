from os.path import join, abspath, dirname
try:
    from setuptools import setup, find_packages
except:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
        name='zs.bibtex',
        author='Horst Gutmann',
        author_email='zerok@zerokspot.com',
        url='https://github.com/zerok/zs.bibtex/',
        license='BSD',
        description='A small collection of bibtex utilities (incl. a minimal parser)',
        long_description = open(join(dirname(abspath(__file__)),'README.rst')).read(),
        version='1.0.0-rc1',
        install_requires=['setuptools', 'pyparsing'],
        namespace_packages=['zs'],
        packages=find_packages('src', exclude=['ez_setup']),
        package_dir = {'': 'src'},
        classifiers=[
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'License :: OSI Approved :: BSD License',
            ]
        )
