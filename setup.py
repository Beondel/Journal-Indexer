from setuptools import setup

setup(name='Journal_Indexer',
      version='1.0',
      description="lightweight journal index which allows entries to be tagged",
      long_description='see readme',
      classifiers=[],
      keywords='',
      author='Ben MacMillan',
      author_email='bengmacmillan@gmail.com',
      url='https://github.com/Beondel/Journal-Indexer',
      license='MIT',
      packages=['Journal_Indexer'],
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      journal = Journal_Indexer.journal_command_runner:main
      """,
)
